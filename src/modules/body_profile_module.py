from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QComboBox,
    QGroupBox,
    QLabel,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from app.layered_body_3d_view import LayeredBody3DView
from core.imodule import IModule


class BodyProfileModule(IModule):
    _LAYERS = [
        (
            "Pele",
            "Primeira camada de visualizacao externa para forma e textura geral.",
        ),
        (
            "Tecido subcutaneo",
            "Camada de gordura e tecido conjuntivo logo abaixo da pele.",
        ),
        (
            "Musculatura",
            "Sistema muscular para movimento, postura e biomecanica basica.",
        ),
        (
            "Esqueleto",
            "Estrutura ossea para suporte e referencia anatomica.",
        ),
        (
            "Orgaos toracicos",
            "Conjunto de orgaos principais na cavidade toracica.",
        ),
        (
            "Coracao e arterias",
            "Foco no sistema cardiovascular central e principais vasos arteriais.",
        ),
    ]

    def __init__(self) -> None:
        self._root: Optional[QWidget] = None
        self._body_type: Optional[QComboBox] = None
        self._description: Optional[QLabel] = None
        self._add_body_button: Optional[QPushButton] = None
        self._body_list: Optional[QListWidget] = None
        self._selected_body_info: Optional[QLabel] = None
        self._layer_slider: Optional[QSlider] = None
        self._layer_name: Optional[QLabel] = None
        self._layer_description: Optional[QLabel] = None
        self._visible_layers: Optional[QLabel] = None
        self._layered_3d_view: Optional[LayeredBody3DView] = None
        self._bodies: list[dict[str, object]] = []
        self._next_body_number = 1

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
        self._on_layer_changed(0)

    def _build_view(self) -> None:
        self._root = QWidget()

        layout = QVBoxLayout(self._root)
        intro = QLabel(
            "Escolhe um perfil corporal, acrescenta corpos e entra por camadas da pele ate ao sistema cardiovascular.",
            self._root,
        )
        intro.setWordWrap(True)

        content_layout = QHBoxLayout()
        controls_layout = QVBoxLayout()

        selection_box = QGroupBox("Perfil base", self._root)
        selection_layout = QVBoxLayout(selection_box)

        self._body_type = QComboBox(selection_box)
        self._body_type.addItems(["Male", "Female", "Neutral"])

        selector_row = QHBoxLayout()
        selector_row.addWidget(self._body_type, 1)

        self._add_body_button = QPushButton("Acrescentar corpo", selection_box)
        selector_row.addWidget(self._add_body_button)

        self._description = QLabel(selection_box)
        self._description.setWordWrap(True)

        selection_layout.addLayout(selector_row)
        selection_layout.addWidget(self._description)

        body_list_box = QGroupBox("Corpos criados", self._root)
        body_list_layout = QVBoxLayout(body_list_box)

        self._body_list = QListWidget(body_list_box)
        self._selected_body_info = QLabel("Nenhum corpo selecionado.", body_list_box)
        self._selected_body_info.setWordWrap(True)

        body_list_layout.addWidget(self._body_list)
        body_list_layout.addWidget(self._selected_body_info)

        layer_box = QGroupBox("Anatomia layer-by-layer", self._root)
        layer_layout = QVBoxLayout(layer_box)

        self._layer_slider = QSlider(Qt.Orientation.Horizontal, layer_box)
        self._layer_slider.setMinimum(0)
        self._layer_slider.setMaximum(len(self._LAYERS) - 1)
        self._layer_slider.setValue(0)

        self._layer_name = QLabel(layer_box)
        self._layer_description = QLabel(layer_box)
        self._layer_description.setWordWrap(True)
        self._visible_layers = QLabel(layer_box)
        self._visible_layers.setWordWrap(True)

        layer_layout.addWidget(self._layer_slider)
        layer_layout.addWidget(self._layer_name)
        layer_layout.addWidget(self._layer_description)
        layer_layout.addWidget(self._visible_layers)

        self._layered_3d_view = LayeredBody3DView(self._root)

        layout.addWidget(intro)
        controls_layout.addWidget(selection_box)
        controls_layout.addWidget(body_list_box)
        controls_layout.addWidget(layer_box)
        controls_layout.addStretch()

        content_layout.addLayout(controls_layout, 2)
        content_layout.addWidget(self._layered_3d_view, 3)

        layout.addLayout(content_layout)
        layout.addStretch()

        self._body_type.currentIndexChanged.connect(self._update_description)
        self._add_body_button.clicked.connect(self._add_body)
        self._body_list.currentRowChanged.connect(self._on_body_selected)
        self._layer_slider.valueChanged.connect(self._on_layer_changed)

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

    def _add_body(self) -> None:
        if self._body_type is None or self._body_list is None or self._layer_slider is None:
            return

        body_name = f"Corpo {self._next_body_number}"
        body_record: dict[str, object] = {
            "name": body_name,
            "type": self._body_type.currentText(),
            "layer_index": self._layer_slider.value(),
        }
        self._bodies.append(body_record)
        self._next_body_number += 1

        self._body_list.addItem(self._format_body_item(body_record))
        self._body_list.setCurrentRow(self._body_list.count() - 1)

    def _on_body_selected(self, index: int) -> None:
        if self._body_list is None or self._selected_body_info is None:
            return

        if index < 0 or index >= len(self._bodies):
            self._selected_body_info.setText("Nenhum corpo selecionado.")
            return

        selected = self._bodies[index]
        layer_index = int(selected["layer_index"])
        if self._layer_slider is not None and self._layer_slider.value() != layer_index:
            self._layer_slider.setValue(layer_index)

        self._refresh_selected_body_info(index)

    def _on_layer_changed(self, index: int) -> None:
        if self._layer_name is None or self._layer_description is None or self._visible_layers is None:
            return

        layer_name, description = self._LAYERS[index]
        self._layer_name.setText(f"Camada ativa: {layer_name}")
        self._layer_description.setText(description)

        visible = " -> ".join(layer[0] for layer in self._LAYERS[: index + 1])
        self._visible_layers.setText(f"Visivel: {visible}")

        if self._layered_3d_view is not None:
            self._layered_3d_view.set_visible_layer(index)

        if self._body_list is None:
            return

        selected_index = self._body_list.currentRow()
        if selected_index < 0 or selected_index >= len(self._bodies):
            return

        self._bodies[selected_index]["layer_index"] = index
        self._refresh_selected_body_info(selected_index)

        selected_item = self._body_list.item(selected_index)
        if selected_item is not None:
            selected_item.setText(self._format_body_item(self._bodies[selected_index]))

    def _refresh_selected_body_info(self, index: int) -> None:
        if self._selected_body_info is None:
            return

        if index < 0 or index >= len(self._bodies):
            self._selected_body_info.setText("Nenhum corpo selecionado.")
            return

        selected = self._bodies[index]
        layer_index = int(selected["layer_index"])
        layer_name = self._LAYERS[layer_index][0]
        self._selected_body_info.setText(
            f"Selecionado: {selected['name']} | Perfil: {selected['type']} | Camada: {layer_name}"
        )

    def _format_body_item(self, body_record: dict[str, object]) -> str:
        layer_name = self._LAYERS[int(body_record["layer_index"])][0]
        return f"{body_record['name']} ({body_record['type']}) - {layer_name}"