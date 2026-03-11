from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QSlider, QVBoxLayout, QWidget

from app.body_preview_widget import BodyPreviewWidget


class BodyRenderLab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Body Render Lab")
        self.resize(560, 820)
        self.setStyleSheet(
            """
            QWidget {
                background: #06235a;
                color: #dce9ff;
                font-size: 13px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #315899;
                height: 6px;
                background: #0f3a80;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #72b8ff;
                border: 1px solid #9ed2ff;
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            """
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        title = QLabel("Body Render Iteration Lab", self)
        title.setStyleSheet("font-size: 20px; font-weight: 700;")

        subtitle = QLabel("Corpo unico para iteracao visual de camadas (sem zoom/pan).", self)
        subtitle.setStyleSheet("color: #9bc0ff;")

        self._preview = BodyPreviewWidget("neutral", self)

        self._layer_name = QLabel("Camada ativa: Pele", self)

        controls = QHBoxLayout()
        controls.setSpacing(10)

        slider_label = QLabel("Layer", self)
        self._slider = QSlider(Qt.Orientation.Horizontal, self)
        self._slider.setMinimum(0)
        self._slider.setMaximum(5)
        self._slider.setValue(0)
        self._slider.valueChanged.connect(self._on_layer_changed)

        controls.addWidget(slider_label)
        controls.addWidget(self._slider, 1)

        root.addWidget(title)
        root.addWidget(subtitle)
        root.addWidget(self._preview, 1)
        root.addLayout(controls)
        root.addWidget(self._layer_name)

    def _on_layer_changed(self, value: int) -> None:
        names = [
            "Pele",
            "Tecido subcutaneo",
            "Musculatura",
            "Esqueleto",
            "Orgaos toracicos",
            "Coracao e arterias",
        ]
        self._preview.set_active_layer(value)
        self._layer_name.setText(f"Camada ativa: {names[value]}")


def main() -> int:
    app = QApplication(sys.argv)
    window = BodyRenderLab()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
