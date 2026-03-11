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
    QCylinderMesh = _resolve_symbol(Qt3DExtras, "QCylinderMesh", "Qt3DExtras.QCylinderMesh")
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
        idle_turn = 1.6 * math.sin(self._pulse * 0.45)
        for entry in self._layer_entities:
            transform = entry["transform"]
            spec: LayerAssetSpec = entry["spec"]
            transform.setScale(spec.base_scale * breath)
            transform.setRotationY(yaw + idle_turn)

    def _setup_camera(self, view3d: object) -> None:
        camera = view3d.camera()
        camera.lens().setPerspectiveProjection(38.0, 1.0, 0.1, 1000.0)

        if self._mode == "skeleton":
            camera.setPosition(QVector3D(0.0, 1.15, 3.5))
        elif self._mode == "fat":
            camera.setPosition(QVector3D(0.9, 1.15, 3.35))
        else:
            camera.setPosition(QVector3D(2.95, 1.1, 0.05))

        camera.setViewCenter(QVector3D(0.0, 0.72, 0.0))

        self._camera_controller = QOrbitCameraController(self._root_entity)
        self._camera_controller.setCamera(camera)
        self._camera_controller.setLinearSpeed(35.0)
        self._camera_controller.setLookSpeed(130.0)

    def _setup_lights(self) -> None:
        light = QEntity(self._root_entity)
        point = QPointLight(light)
        point.setColor(QColor(236, 248, 255))
        point.setIntensity(1.95)
        t = QTransform(light)
        t.setTranslation(QVector3D(3.8, 4.8, 3.8))
        light.addComponent(point)
        light.addComponent(t)

        fill = QEntity(self._root_entity)
        fill_light = QPointLight(fill)
        fill_light.setColor(QColor(145, 176, 235))
        fill_light.setIntensity(1.05)
        fill_t = QTransform(fill)
        fill_t.setTranslation(QVector3D(-3.7, 2.0, 2.6))
        fill.addComponent(fill_light)
        fill.addComponent(fill_t)

        rim = QEntity(self._root_entity)
        rim_light = QPointLight(rim)
        rim_light.setColor(QColor(104, 166, 255))
        rim_light.setIntensity(0.85)
        rim_t = QTransform(rim)
        rim_t.setTranslation(QVector3D(-1.8, 2.3, -3.5))
        rim.addComponent(rim_light)
        rim.addComponent(rim_t)

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
            material.setAmbient(color.darker(128))
        if hasattr(material, "setSpecular"):
            material.setSpecular(QColor(218, 232, 255))
        if hasattr(material, "setShininess"):
            material.setShininess(28.0)
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

    def _add_cylinder_part(
        self,
        parent: object,
        color: QColor,
        radius: float,
        length: float,
        position: QVector3D,
    ) -> dict[str, object]:
        part = QEntity(parent)
        mesh = QCylinderMesh(part)
        mesh.setRadius(radius)
        mesh.setLength(length)
        mesh.setRings(28)
        mesh.setSlices(28)

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
        profile = {
            "skeleton": {
                "head": 0.135,
                "neck_r": 0.034,
                "torso_r": 0.145,
                "torso_h": 0.70,
                "pelvis": 0.155,
                "arm_r": 0.045,
                "forearm_r": 0.040,
                "leg_r": 0.052,
                "calf_r": 0.046,
                "shoulder_x": 0.22,
            },
            "fat": {
                "head": 0.165,
                "neck_r": 0.052,
                "torso_r": 0.250,
                "torso_h": 0.80,
                "pelvis": 0.240,
                "arm_r": 0.088,
                "forearm_r": 0.078,
                "leg_r": 0.108,
                "calf_r": 0.095,
                "shoulder_x": 0.30,
            },
            "muscle": {
                "head": 0.152,
                "neck_r": 0.050,
                "torso_r": 0.205,
                "torso_h": 0.76,
                "pelvis": 0.195,
                "arm_r": 0.080,
                "forearm_r": 0.068,
                "leg_r": 0.090,
                "calf_r": 0.078,
                "shoulder_x": 0.285,
            },
        }[self._mode]

        core = color
        mid = color.darker(114)
        joint = color.darker(132)

        parts: list[dict[str, object]] = []

        parts.append(self._add_sphere_part(parent, core, profile["head"], QVector3D(0.0, 1.70, 0.0)))
        parts.append(
            self._add_cylinder_part(parent, mid, profile["neck_r"], 0.15, QVector3D(0.0, 1.50, 0.0))
        )
        parts.append(
            self._add_cylinder_part(
                parent,
                core,
                profile["torso_r"],
                profile["torso_h"],
                QVector3D(0.0, 1.03, 0.0),
            )
        )
        parts.append(self._add_sphere_part(parent, mid, profile["pelvis"], QVector3D(0.0, 0.56, 0.0)))

        parts.append(
            self._add_sphere_part(parent, joint, profile["arm_r"] * 1.15, QVector3D(-profile["shoulder_x"], 1.30, 0.0))
        )
        parts.append(
            self._add_sphere_part(parent, joint, profile["arm_r"] * 1.15, QVector3D(profile["shoulder_x"], 1.30, 0.0))
        )

        parts.append(
            self._add_cylinder_part(
                parent,
                core,
                profile["arm_r"],
                0.50,
                QVector3D(-profile["shoulder_x"], 1.00, 0.0),
            )
        )
        parts.append(
            self._add_cylinder_part(
                parent,
                core,
                profile["arm_r"],
                0.50,
                QVector3D(profile["shoulder_x"], 1.00, 0.0),
            )
        )

        parts.append(
            self._add_sphere_part(parent, joint, profile["arm_r"] * 1.02, QVector3D(-profile["shoulder_x"], 0.74, 0.0))
        )
        parts.append(
            self._add_sphere_part(parent, joint, profile["arm_r"] * 1.02, QVector3D(profile["shoulder_x"], 0.74, 0.0))
        )
        parts.append(
            self._add_cylinder_part(
                parent,
                core,
                profile["forearm_r"],
                0.44,
                QVector3D(-profile["shoulder_x"], 0.48, 0.0),
            )
        )
        parts.append(
            self._add_cylinder_part(
                parent,
                core,
                profile["forearm_r"],
                0.44,
                QVector3D(profile["shoulder_x"], 0.48, 0.0),
            )
        )

        parts.append(
            self._add_sphere_part(parent, mid, profile["forearm_r"] * 1.08, QVector3D(-profile["shoulder_x"], 0.22, 0.03))
        )
        parts.append(
            self._add_sphere_part(parent, mid, profile["forearm_r"] * 1.08, QVector3D(profile["shoulder_x"], 0.22, 0.03))
        )

        hip_x = 0.14 if self._mode != "fat" else 0.16
        parts.append(
            self._add_cylinder_part(parent, core, profile["leg_r"], 0.52, QVector3D(-hip_x, 0.24, 0.0))
        )
        parts.append(
            self._add_cylinder_part(parent, core, profile["leg_r"], 0.52, QVector3D(hip_x, 0.24, 0.0))
        )
        parts.append(self._add_sphere_part(parent, joint, profile["leg_r"] * 0.98, QVector3D(-hip_x, -0.04, 0.0)))
        parts.append(self._add_sphere_part(parent, joint, profile["leg_r"] * 0.98, QVector3D(hip_x, -0.04, 0.0)))
        parts.append(
            self._add_cylinder_part(parent, core, profile["calf_r"], 0.46, QVector3D(-hip_x, -0.29, 0.0))
        )
        parts.append(
            self._add_cylinder_part(parent, core, profile["calf_r"], 0.46, QVector3D(hip_x, -0.29, 0.0))
        )
        parts.append(
            self._add_box_part(
                parent,
                mid,
                profile["calf_r"] * 1.4,
                profile["calf_r"] * 0.45,
                profile["calf_r"] * 2.2,
                QVector3D(-hip_x, -0.55, 0.05),
            )
        )
        parts.append(
            self._add_box_part(
                parent,
                mid,
                profile["calf_r"] * 1.4,
                profile["calf_r"] * 0.45,
                profile["calf_r"] * 2.2,
                QVector3D(hip_x, -0.55, 0.05),
            )
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
                color = base.lighter(165)
            elif spec.layer_index == focus:
                color = base.lighter(135)
            else:
                color = base.darker(118)

            for material in materials:
                material.setDiffuse(color)
