from __future__ import annotations

import math
from typing import Literal

from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor, QVector3D
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from core.anatomy_assets import ACTIVE_ASSET_CATALOG, LayerAssetSpec

BodyMode = Literal["skeleton", "fat", "muscle"]


def _resolve_symbol(module: object, *names: str) -> object:
    for name in names:
        symbol = getattr(module, name, None)
        if symbol is not None:
            return symbol
    raise AttributeError(f"Missing Qt3D symbol candidates: {', '.join(names)}")


try:
    from PySide6 import Qt3DCore, Qt3DExtras, Qt3DRender

    QEntity = _resolve_symbol(Qt3DCore, "QEntity", "Qt3DCore.QEntity")
    QTransform = _resolve_symbol(Qt3DCore, "QTransform", "Qt3DCore.QTransform")

    Qt3DWindow = _resolve_symbol(Qt3DExtras, "Qt3DWindow", "Qt3DExtras.Qt3DWindow")
    QOrbitCameraController = _resolve_symbol(
        Qt3DExtras,
        "QOrbitCameraController",
        "Qt3DExtras.QOrbitCameraController",
    )
    QPhongMaterial = _resolve_symbol(Qt3DExtras, "QPhongMaterial", "Qt3DExtras.QPhongMaterial")
    QCuboidMesh = _resolve_symbol(Qt3DExtras, "QCuboidMesh", "Qt3DExtras.QCuboidMesh")
    QSphereMesh = _resolve_symbol(Qt3DExtras, "QSphereMesh", "Qt3DExtras.QSphereMesh")

    QPointLight = _resolve_symbol(Qt3DRender, "QPointLight", "Qt3DRender.QPointLight")

    QT3D_AVAILABLE = True
    QT3D_IMPORT_ERROR = ""
except Exception as exc:
    QT3D_AVAILABLE = False
    QT3D_IMPORT_ERROR = str(exc)


class BodyPreviewWidget(QWidget):
    def __init__(self, mode: BodyMode, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._mode = mode
        self._active_layer = 0
        self._pulse = 0.0
        self._root_entity: object | None = None
        self._layer_entities: list[dict[str, object]] = []
        self._container: QWidget | None = None
        self._view3d: object | None = None
        self._camera_controller: object | None = None
        self._timer = QTimer(self)

        self.setMinimumSize(220, 360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if not QT3D_AVAILABLE:
            fallback = QLabel(f"Qt3D indisponivel: {QT3D_IMPORT_ERROR}", self)
            fallback.setWordWrap(True)
            layout.addWidget(fallback)
            return

        self._view3d = Qt3DWindow()
        if hasattr(self._view3d, "defaultFrameGraph"):
            frame_graph = self._view3d.defaultFrameGraph()
            if frame_graph is not None and hasattr(frame_graph, "setClearColor"):
                frame_graph.setClearColor(QColor(8, 34, 84))

        self._container = QWidget.createWindowContainer(self._view3d, self)
        layout.addWidget(self._container, 1)

        self._root_entity = QEntity()
        self._view3d.setRootEntity(self._root_entity)

        self._setup_camera(self._view3d)
        self._setup_lights()
        self._build_layer_entities()
        self.set_active_layer(0)

        self._timer.timeout.connect(self._tick)
        self._timer.start(45)

    def set_active_layer(self, layer_index: int) -> None:
        self._active_layer = layer_index
        self._refresh_layers()

    def _tick(self) -> None:
        self._pulse += 0.06

        breath = 1.0 + 0.012 * (0.5 + 0.5 * math.sin(self._pulse))
        yaw = ACTIVE_ASSET_CATALOG.pose_yaw_for_mode(self._mode)
        for entry in self._layer_entities:
            transform = entry["transform"]
            spec: LayerAssetSpec = entry["spec"]
            transform.setScale(spec.base_scale * breath)
            transform.setRotationY(yaw)

    def _setup_camera(self, view3d: object) -> None:
        camera = view3d.camera()
        camera.lens().setPerspectiveProjection(45.0, 1.0, 0.1, 1000.0)

        if self._mode == "skeleton":
            camera.setPosition(QVector3D(0.0, 1.3, 7.0))
        elif self._mode == "fat":
            camera.setPosition(QVector3D(2.4, 1.4, 6.8))
        else:
            camera.setPosition(QVector3D(5.0, 1.2, 0.0))

        camera.setViewCenter(QVector3D(0.0, 0.8, 0.0))

        self._camera_controller = QOrbitCameraController(self._root_entity)
        self._camera_controller.setCamera(camera)
        self._camera_controller.setLinearSpeed(35.0)
        self._camera_controller.setLookSpeed(130.0)

    def _setup_lights(self) -> None:
        light = QEntity(self._root_entity)
        point = QPointLight(light)
        point.setColor(QColor(224, 244, 255))
        point.setIntensity(1.4)
        t = QTransform(light)
        t.setTranslation(QVector3D(4.5, 6.0, 6.5))
        light.addComponent(point)
        light.addComponent(t)

        fill = QEntity(self._root_entity)
        fill_light = QPointLight(fill)
        fill_light.setColor(QColor(150, 190, 255))
        fill_light.setIntensity(0.7)
        fill_t = QTransform(fill)
        fill_t.setTranslation(QVector3D(-5.0, 2.0, -4.0))
        fill.addComponent(fill_light)
        fill.addComponent(fill_t)

    def _build_layer_entities(self) -> None:
        for spec in ACTIVE_ASSET_CATALOG.layer_specs():
            entity = QEntity(self._root_entity)

            transform = QTransform(entity)
            transform.setScale(spec.base_scale)
            transform.setTranslation(QVector3D(0.0, 0.25, 0.0))
            transform.setRotationY(ACTIVE_ASSET_CATALOG.pose_yaw_for_mode(self._mode))
            entity.addComponent(transform)

            model = self._build_procedural_humanoid(entity, QColor(*spec.rgb))

            self._layer_entities.append(
                {
                    "spec": spec,
                    "entity": entity,
                    "materials": model["materials"],
                    "parts": model["parts"],
                    "transform": transform,
                }
            )

    def _make_material(self, parent: object, color: QColor) -> object:
        material = QPhongMaterial(parent)
        material.setDiffuse(color)
        if hasattr(material, "setAmbient"):
            material.setAmbient(QColor(28, 40, 66))
        if hasattr(material, "setShininess"):
            material.setShininess(18.0)
        return material

    def _add_box_part(
        self,
        parent: object,
        color: QColor,
        x_extent: float,
        y_extent: float,
        z_extent: float,
        position: QVector3D,
    ) -> dict[str, object]:
        part = QEntity(parent)
        mesh = QCuboidMesh(part)
        mesh.setXExtent(x_extent)
        mesh.setYExtent(y_extent)
        mesh.setZExtent(z_extent)

        material = self._make_material(part, color)

        transform = QTransform(part)
        transform.setTranslation(position)

        part.addComponent(mesh)
        part.addComponent(material)
        part.addComponent(transform)
        return {
            "entity": part,
            "mesh": mesh,
            "material": material,
            "transform": transform,
        }

    def _add_sphere_part(
        self,
        parent: object,
        color: QColor,
        radius: float,
        position: QVector3D,
    ) -> dict[str, object]:
        part = QEntity(parent)
        mesh = QSphereMesh(part)
        mesh.setRadius(radius)

        material = self._make_material(part, color)

        transform = QTransform(part)
        transform.setTranslation(position)

        part.addComponent(mesh)
        part.addComponent(material)
        part.addComponent(transform)
        return {
            "entity": part,
            "mesh": mesh,
            "material": material,
            "transform": transform,
        }

    def _build_procedural_humanoid(self, parent: object, color: QColor) -> dict[str, list[object]]:
        parts: list[dict[str, object]] = []

        parts.append(self._add_sphere_part(parent, color, 0.19, QVector3D(0.0, 1.68, 0.0)))
        parts.append(
            self._add_box_part(parent, color, 0.58, 0.82, 0.30, QVector3D(0.0, 1.05, 0.0))
        )
        parts.append(
            self._add_box_part(parent, color, 0.52, 0.24, 0.30, QVector3D(0.0, 0.55, 0.0))
        )

        parts.append(
            self._add_box_part(parent, color, 0.18, 0.68, 0.18, QVector3D(-0.45, 1.03, 0.0))
        )
        parts.append(
            self._add_box_part(parent, color, 0.18, 0.68, 0.18, QVector3D(0.45, 1.03, 0.0))
        )
        parts.append(
            self._add_box_part(parent, color, 0.15, 0.48, 0.15, QVector3D(-0.48, 0.55, 0.0))
        )
        parts.append(
            self._add_box_part(parent, color, 0.15, 0.48, 0.15, QVector3D(0.48, 0.55, 0.0))
        )

        parts.append(
            self._add_box_part(parent, color, 0.19, 0.50, 0.19, QVector3D(-0.14, 0.22, 0.0))
        )
        parts.append(
            self._add_box_part(parent, color, 0.19, 0.50, 0.19, QVector3D(0.14, 0.22, 0.0))
        )
        parts.append(
            self._add_box_part(parent, color, 0.16, 0.46, 0.16, QVector3D(-0.14, -0.26, 0.0))
        )
        parts.append(
            self._add_box_part(parent, color, 0.16, 0.46, 0.16, QVector3D(0.14, -0.26, 0.0))
        )

        return {
            "parts": parts,
            "materials": [part["material"] for part in parts],
        }

    def _refresh_layers(self) -> None:
        focus = ACTIVE_ASSET_CATALOG.focus_layer_for_mode(self._mode)
        for entry in self._layer_entities:
            spec: LayerAssetSpec = entry["spec"]
            entity = entry["entity"]
            materials = entry["materials"]

            visible = spec.layer_index <= self._active_layer
            entity.setEnabled(visible)
            if not visible:
                continue

            base = QColor(*spec.rgb)
            if spec.layer_index == self._active_layer:
                color = base.lighter(145)
            elif spec.layer_index == focus:
                color = base.lighter(122)
            else:
                color = base.darker(132)

            for material in materials:
                material.setDiffuse(color)
