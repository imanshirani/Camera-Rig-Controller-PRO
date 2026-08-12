from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSlider, QSpinBox, QDoubleSpinBox,
)
from PySide6.QtCore import Qt, Signal


class SliderSpinRow(QWidget):
    """Label + slider + spinbox that stay in sync, emits valueChanged(float)."""
    valueChanged = Signal(float)

    def __init__(self, label: str, min_val: float, max_val: float,
                 default: float, decimals: int = 1, unit: str = "",
                 parent=None):
        super().__init__(parent)
        self._decimals = decimals
        self._factor   = 10 ** decimals

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 4)
        outer.setSpacing(3)

        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        lbl = QLabel(label)
        lbl.setObjectName("lbl_section")
        top.addWidget(lbl)
        top.addStretch()

        if decimals == 0:
            self._spin = QSpinBox()
            self._spin.setRange(int(min_val), int(max_val))
            self._spin.setValue(int(default))
            if unit:
                self._spin.setSuffix(unit)
        else:
            self._spin = QDoubleSpinBox()
            self._spin.setRange(min_val, max_val)
            self._spin.setDecimals(decimals)
            self._spin.setValue(default)
            if unit:
                self._spin.setSuffix(unit)
        self._spin.setFixedWidth(90)
        top.addWidget(self._spin)
        outer.addLayout(top)

        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(int(min_val * self._factor), int(max_val * self._factor))
        self._slider.setValue(int(default * self._factor))
        outer.addWidget(self._slider)

        self._slider.valueChanged.connect(self._on_slider)
        self._spin.valueChanged.connect(self._on_spin)

    def _on_slider(self, v: int):
        val = v / self._factor
        self._spin.blockSignals(True)
        if self._decimals == 0:
            self._spin.setValue(int(round(val)))
        else:
            self._spin.setValue(val)
        self._spin.blockSignals(False)
        self.valueChanged.emit(float(self._spin.value()))

    def _on_spin(self, v):
        self._slider.blockSignals(True)
        self._slider.setValue(int(float(v) * self._factor))
        self._slider.blockSignals(False)
        self.valueChanged.emit(float(v))

    @property
    def value(self) -> float:
        return float(self._spin.value())

    @value.setter
    def value(self, v: float):
        self._slider.blockSignals(True)
        self._spin.blockSignals(True)
        if self._decimals == 0:
            self._spin.setValue(int(round(v)))
        else:
            self._spin.setValue(float(v))
        self._slider.setValue(int(float(v) * self._factor))
        self._slider.blockSignals(False)
        self._spin.blockSignals(False)

    def blockAll(self, block: bool):
        self._slider.blockSignals(block)
        self._spin.blockSignals(block)
