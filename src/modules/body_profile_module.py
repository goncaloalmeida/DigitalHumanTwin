from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from app.body_preview_widget import BodyPreviewWidget
from core.anatomy_provider import ACTIVE_ANATOMY_PROVIDER
from core.imodule import IModule


class BodyProfileModule(IModule):
    _LAYERS = [
        ("Pele", "Camada externa visual."),
        ("Tecido subcutaneo", "Camada de gordura e tecido conjuntivo."),
        ("Musculatura", "Sistema muscular para movimento."),
        ("Esqueleto", "Estrutura ossea de suporte."),
        ("Orgaos toracicos", "Orgaos internos principais."),
        ("Coracao e arterias", "Foco cardiovascular central."),
    ]

    def __init__(self) -> None:
        self._root: Optional[QWidget] = None
        self._description: Optional[QLabel] = None
        self._body_info: Optional[QLabel] = None
        self._layer_slider: Optional[QSlider] = None
        self._layer_name: Optional[QLabel] = None
        self._visible_layers: Optional[QLabel] = None
        self._create_body_button: Optional[QPushButton] = None
        self._layer_checkboxes: list[QCheckBox] = []
        self._syncing_layer_controls = False
        self._current_body: Optional[dict[str, object]] = None

        self._body_preview: Optional[BodyPreviewWidget] = None

        self._organ_value_labels: dict[str, QLabel] = {}

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
        self._create_or_reset_body()
        self._on_layer_changed(0)

    def _build_view(self) -> None:
        self._root = QWidget()
        self._root.setObjectName("dashboardRoot")
        self._root.setStyleSheet(
            """
            QWidget#dashboardRoot {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #051a46, stop:0.5 #09285f, stop:1 #051b46);
                color: #d7e7ff;
            }
            QGroupBox {
                border: 1px solid #2d4c8a;
                border-radius: 10px;
                margin-top: 10px;
                font-weight: 600;
                color: #dce9ff;
                background-color: rgba(7, 31, 74, 105);
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
            QLabel { color: #d7e7ff; }
            QFrame#metricCard {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #10367e, stop:1 #0a2a68);
                border: 1px solid #3b62a8;
                border-radius: 10px;
            }
            QPushButton { background-color: #1d4da0; color: #e7f1ff; border: 1px solid #3a73d0; border-radius: 6px; padding: 7px 10px; }
            QPushButton:hover { background-color: #2562c6; }
            QSlider::groove:horizontal { border: 1px solid #294a88; height: 6px; background: #103271; border-radius: 3px; }
            QSlider::handle:horizontal { background: #6ab3ff; border: 1px solid #8fcdff; width: 14px; margin: -5px 0; border-radius: 7px; }
            """
        )

        root_layout = QVBoxLayout(self._root)
        root_layout.setSpacing(10)
        root_layout.setContentsMargins(12, 12, 12, 12)

        header = self._build_header()
        controls = self._build_layer_controls()

        content_row = QHBoxLayout()
        content_row.setSpacing(12)

        left_col = QVBoxLayout()
        left_col.setSpacing(10)
        left_col.addLayout(self._build_body_cards())
        left_col.addWidget(self._build_timeline_box())

        right_col = self._build_organs_panel()

        content_row.addLayout(left_col, 3)
        content_row.addWidget(right_col, 1)

        root_layout.addWidget(header)
        root_layout.addWidget(controls)
        root_layout.addLayout(content_row, 1)

    def _build_header(self) -> QWidget:
        header = QFrame(self._root)
        header_layout = QVBoxLayout(header)

        top_row = QHBoxLayout()

        name = QLabel("Goncalo Almeida", header)
        name.setStyleSheet("font-size: 24px; font-weight: 700;")

        meta = QLabel("Gender: Neutral    Language: Portuguese    Ethnicity: Not set", header)
        meta.setStyleSheet("color: #8fb3ef; font-size: 12px;")

        source = QLabel(
            f"Data source: {ACTIVE_ANATOMY_PROVIDER.name} ({ACTIVE_ANATOMY_PROVIDER.license_name})",
            header,
        )
        source.setStyleSheet("color: #9ac3ff; font-size: 12px;")

        top_row.addWidget(name)
        top_row.addStretch()
        top_row.addWidget(meta)

        header_layout.addLayout(top_row)
        header_layout.addWidget(source)

        return header

    def _build_layer_controls(self) -> QWidget:
        box = QGroupBox("Corpo ativo", self._root)
        layout = QVBoxLayout(box)

        self._description = QLabel(
            "Perfil unico Neutral para simplificar prototipagem e validacao iterativa.",
            box,
        )
        self._create_body_button = QPushButton("Criar/Reiniciar corpo neutral", box)
        self._body_info = QLabel("Nenhum corpo inicializado.", box)

        layer_group = QGroupBox("Anatomia layer-by-layer", box)
        layer_layout = QVBoxLayout(layer_group)

        self._layer_slider = QSlider(Qt.Orientation.Horizontal, layer_group)
        self._layer_slider.setMinimum(0)
        self._layer_slider.setMaximum(len(self._LAYERS) - 1)
        self._layer_slider.setValue(0)

        checks = QHBoxLayout()
        for index, (layer_name, _) in enumerate(self._LAYERS):
            checkbox = QCheckBox(layer_name, layer_group)
            checkbox.setChecked(index == 0)
            checkbox.toggled.connect(
                lambda checked, layer_index=index: self._on_layer_checkbox_toggled(
                    layer_index, checked
                )
            )
            checks.addWidget(checkbox)
            self._layer_checkboxes.append(checkbox)

        self._layer_name = QLabel(layer_group)
        self._visible_layers = QLabel(layer_group)

        layer_layout.addWidget(self._layer_slider)
        layer_layout.addLayout(checks)
        layer_layout.addWidget(self._layer_name)
        layer_layout.addWidget(self._visible_layers)

        layout.addWidget(self._description)
        layout.addWidget(self._create_body_button)
        layout.addWidget(self._body_info)
        layout.addWidget(layer_group)

        self._create_body_button.clicked.connect(self._create_or_reset_body)
        self._layer_slider.valueChanged.connect(self._on_layer_changed)

        return box

    def _build_body_cards(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(10)

        self._body_preview = BodyPreviewWidget("neutral", self._root)

        row.addWidget(
            self._build_body_card("BODY", self._body_preview, "Camadas", "Visualizacao unica layer-by-layer"),
            1,
        )

        return row

    def _build_body_card(
        self,
        title: str,
        preview: BodyPreviewWidget,
        metric_label: str,
        metric_value: str,
    ) -> QWidget:
        card = QFrame(self._root)
        card.setObjectName("metricCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 12)
        layout.setSpacing(8)
        layout.addWidget(preview, 1)

        title_label = QLabel(title, card)
        title_label.setStyleSheet("font-size: 18px; font-weight: 700; letter-spacing: 0.7px;")

        metric = QLabel(f"{metric_label}: {metric_value}", card)
        metric.setStyleSheet("color: #9bc0ff; font-size: 12px;")

        layout.addWidget(title_label)
        layout.addWidget(metric)
        return card

    def _build_organs_panel(self) -> QWidget:
        panel = QGroupBox("Scanned Organs", self._root)
        panel_layout = QVBoxLayout(panel)

        organ_defs = [
            ("BRAIN", "Volume", "1,207 cm3"),
            ("HEART", "Ejection Fraction", "45 %"),
            ("LUNGS", "Max. Volume", "6,212 cm3"),
            ("LIVER", "Volume", "2,098 cm3"),
        ]

        for organ_name, metric_name, base_value in organ_defs:
            card = QFrame(panel)
            card.setObjectName("metricCard")
            card_layout = QVBoxLayout(card)

            organ_title = QLabel(organ_name, card)
            organ_title.setStyleSheet("font-size: 14px; font-weight: 700;")
            metric_title = QLabel(metric_name, card)
            metric_title.setStyleSheet("color: #8fb3ef; font-size: 11px;")
            metric_value = QLabel(base_value, card)
            metric_value.setStyleSheet("font-size: 16px; font-weight: 700;")

            card_layout.addWidget(organ_title)
            card_layout.addWidget(metric_title)
            card_layout.addWidget(metric_value)

            panel_layout.addWidget(card)
            self._organ_value_labels[organ_name] = metric_value

        panel_layout.addStretch()
        return panel

    def _build_timeline_box(self) -> QWidget:
        box = QGroupBox("Medical History", self._root)
        layout = QVBoxLayout(box)

        labels = QLabel("46 Events Found | 2019 -> 2020", box)
        labels.setStyleSheet("color: #8fb3ef; font-size: 12px;")

        points_row = QGridLayout()
        points_row.setHorizontalSpacing(8)

        for index in range(20):
            dot = QLabel("o", box)
            dot.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if index in {1, 7, 12, 18}:
                dot.setStyleSheet("color: #8fd0ff; font-size: 20px;")
            else:
                dot.setStyleSheet("color: #5f83bf; font-size: 14px;")
            points_row.addWidget(dot, 0, index)

        layout.addWidget(labels)
        layout.addLayout(points_row)
        return box

    def _create_or_reset_body(self) -> None:
        if self._layer_slider is None:
            return

        self._current_body = {
            "name": "Corpo Neutral",
            "layer_index": self._layer_slider.value(),
        }
        self._refresh_body_info()

    def _on_layer_changed(self, index: int) -> None:
        if self._layer_name is None or self._visible_layers is None:
            return

        layer_name, _ = self._LAYERS[index]
        self._layer_name.setText(f"Camada ativa: {layer_name}")

        visible = " -> ".join(layer[0] for layer in self._LAYERS[: index + 1])
        self._visible_layers.setText(f"Visivel: {visible}")

        self._syncing_layer_controls = True
        for layer_index, checkbox in enumerate(self._layer_checkboxes):
            checkbox.setChecked(layer_index <= index)
        self._syncing_layer_controls = False

        if self._current_body is None:
            self._create_or_reset_body()
        else:
            self._current_body["layer_index"] = index
            self._refresh_body_info()

        if self._body_preview is not None:
            self._body_preview.set_active_layer(index)

        self._update_organs_metrics(index)

    def _on_layer_checkbox_toggled(self, layer_index: int, checked: bool) -> None:
        if self._syncing_layer_controls or self._layer_slider is None:
            return

        if layer_index == 0 and not checked:
            self._syncing_layer_controls = True
            self._layer_checkboxes[0].setChecked(True)
            self._syncing_layer_controls = False
            return

        if checked:
            self._layer_slider.setValue(layer_index)
            return

        self._layer_slider.setValue(max(0, layer_index - 1))

    def _refresh_body_info(self) -> None:
        if self._body_info is None:
            return

        if self._current_body is None:
            self._body_info.setText("Nenhum corpo inicializado.")
            return

        layer_index = int(self._current_body["layer_index"])
        layer_name = self._LAYERS[layer_index][0]
        self._body_info.setText(f"Ativo: {self._current_body['name']} | Perfil: Neutral | Camada: {layer_name}")

    def _update_organs_metrics(self, layer_index: int) -> None:
        values = ACTIVE_ANATOMY_PROVIDER.organ_metrics(layer_index)

        for organ_name, label in self._organ_value_labels.items():
            label.setText(values[organ_name])