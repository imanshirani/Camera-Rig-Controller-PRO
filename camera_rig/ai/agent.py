"""Camera Rig AI Agent — supports Claude API and local OpenAI-compatible models."""
import json
import urllib.request
import urllib.error
from camera_rig.ai.tools import CAMERA_RIG_TOOLS, SYSTEM_PROMPT

# Convert Claude-format tools to OpenAI format for local models
_OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["input_schema"],
        }
    }
    for t in CAMERA_RIG_TOOLS
]


class ClaudeAgent:
    """Claude API client — uses Anthropic messages API with tool calling."""

    API_URL = "https://api.anthropic.com/v1/messages"

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5"):
        self.api_key = api_key
        self.model   = model
        self.history = []

    def clear_history(self):
        self.history = []

    def chat(self, user_message: str, rig_state_text: str, executor) -> str:
        if not self.api_key or not self.api_key.strip():
            return "⚠️ No API key. Enter your Anthropic API key in Settings."

        system = SYSTEM_PROMPT + f"\n\n--- CURRENT RIG STATE ---\n{rig_state_text}"
        self.history.append({"role": "user", "content": user_message})

        while True:
            response = self._call_api(system, self.history)
            if response is None:
                self.history.pop()
                return "⚠️ API call failed. Check your key and internet connection."

            stop_reason = response.get("stop_reason", "")
            content     = response.get("content", [])
            text_parts, tool_uses = [], []
            for block in content:
                if block.get("type") == "text":
                    text_parts.append(block["text"])
                elif block.get("type") == "tool_use":
                    tool_uses.append(block)

            self.history.append({"role": "assistant", "content": content})

            if stop_reason != "tool_use" or not tool_uses:
                return "\n".join(text_parts) if text_parts else "Done."

            tool_results = []
            for tu in tool_uses:
                result = executor.execute(tu["name"], tu.get("input", {}))
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tu["id"],
                    "content": result,
                })
            self.history.append({"role": "user", "content": tool_results})

    def _call_api(self, system: str, messages: list):
        payload = json.dumps({
            "model":      self.model,
            "max_tokens": 1024,
            "system":     system,
            "tools":      CAMERA_RIG_TOOLS,
            "messages":   messages,
        }).encode("utf-8")
        req = urllib.request.Request(
            self.API_URL, data=payload, method="POST",
            headers={
                "Content-Type":      "application/json",
                "x-api-key":         self.api_key,
                "anthropic-version": "2023-06-01",
            }
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            print(f"[AI-Claude] HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:300]}")
        except Exception as e:
            print(f"[AI-Claude] Error: {e}")
        return None


class LocalModelAgent:
    """
    OpenAI-compatible local model client.
    Works with Ollama (http://localhost:11434/v1) and LM Studio (http://localhost:1234/v1).
    """

    def __init__(self, base_url: str = "http://localhost:11434/v1",
                 model: str = "llama3.1"):
        self.base_url = base_url.rstrip("/")
        self.model    = model
        self.history  = []

    def clear_history(self):
        self.history = []

    def chat(self, user_message: str, rig_state_text: str, executor) -> str:
        system = SYSTEM_PROMPT + f"\n\n--- CURRENT RIG STATE ---\n{rig_state_text}"
        self.history.append({"role": "user", "content": user_message})

        while True:
            messages = [{"role": "system", "content": system}] + self.history
            response = self._call_api(messages)
            if response is None:
                self.history.pop()
                return "⚠️ Local model call failed. Is Ollama/LM Studio running?"

            choices = response.get("choices", [])
            if not choices:
                self.history.pop()
                return "⚠️ Empty response from local model."

            choice  = choices[0]
            message = choice.get("message", {})
            finish  = choice.get("finish_reason", "stop")
            content = message.get("content") or ""
            tool_calls = message.get("tool_calls") or []

            self.history.append({
                "role": "assistant",
                "content": content,
                "tool_calls": tool_calls if tool_calls else None,
            })

            if finish != "tool_calls" or not tool_calls:
                return content if content else "Done."

            # Execute tool calls
            for tc in tool_calls:
                fn   = tc.get("function", {})
                name = fn.get("name", "")
                try:
                    args = json.loads(fn.get("arguments", "{}"))
                except Exception:
                    args = {}
                result = executor.execute(name, args)
                self.history.append({
                    "role":         "tool",
                    "tool_call_id": tc.get("id", ""),
                    "content":      result,
                })

    def _call_api(self, messages: list):
        payload = json.dumps({
            "model":    self.model,
            "messages": messages,
            "tools":    _OPENAI_TOOLS,
            "stream":   False,
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=payload, method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            print(f"[AI-Local] HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:300]}")
        except Exception as e:
            print(f"[AI-Local] Error: {e}")
        return None


# ── Factory ───────────────────────────────────────────────────────────────────

def create_agent(provider: str, **kwargs):
    """
    provider: "claude" | "local"
    kwargs for claude: api_key, model (optional)
    kwargs for local:  base_url, model
    """
    if provider == "claude":
        return ClaudeAgent(
            api_key=kwargs.get("api_key", ""),
            model=kwargs.get("model", "claude-sonnet-4-5"),
        )
    return LocalModelAgent(
        base_url=kwargs.get("base_url", "http://localhost:11434/v1"),
        model=kwargs.get("model", "llama3.1"),
    )
