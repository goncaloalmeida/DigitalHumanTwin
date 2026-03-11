from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from core.imodule import IModule


class BodyProfileModule(IModule):
    def __init__(self) -> None:
        self._root: Optional[QWidget] = None
        self._body_type: Optional[QComboBox] = None
        self._description: Optional[QLabel] = None

    def id(self) -> str:
        return "body-profile"

    def display_name(self) -> str:
        return "Body Profile"

    def view(self) -> QWidget:
        if self._root is None:
            self._build_view()
        return self._root

    def initialize(self) -> None:
        self.view()
        self._update_description(0)

    def _build_view(self) -> None:
        self._root = QWidget()

        layout = QVBoxLayout(self._root)
        intro = QLabel(
            "Simple sample module for choosing the base body profile.",
            self._root,
        )
        intro.setWordWrap(True)

        selection_box = QGroupBox("Body type", self._root)
        selection_layout = QVBoxLayout(selection_box)

        self._body_type = QComboBox(selection_box)
        self._body_type.addItems(["Male", "Female", "Neutral"])

        self._description = QLabel(selection_box)
        self._description.setWordWrap(True)

        selection_layout.addWidget(self._body_type)
        selection_layout.addWidget(self._description)

        layout.addWidget(intro)
        layout.addWidget(selection_box)
        layout.addStretch()

        self._body_type.currentIndexChanged.connect(self._update_description)

    def _update_description(self, index: int) -> None:
        if self._description is None:
            return

        if index == 0:
            self._description.setText("Base preset for an adult male body model.")
            return

        if index == 1:
            self._description.setText("Base preset for an adult female body model.")
            return

        self._description.setText(
            "Neutral preset for early prototyping and shared testing."
        )