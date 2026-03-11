from __future__ import annotations

import math
from typing import Literal

from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor, QVector3D
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from core.anatomy_assets import ACTIVE_ASSET_CATALOG, LayerAssetSpec

BodyMode = Literal["skeleton", "fat", "muscle", "neutral"]
MaterialEntry = dict[str, object]
PartEntry = dict[str, object]


def _resolve_symbol(module: object, *names: str) -> object:
    for name in names:
        symbol = getattr(module, name, None)
        if symbol is not None:
            return symbol
    raise AttributeError(f"Missing Qt3D symbol candidates: {', '.join(names)}")


def _resolve_optional_symbol(module: object, *names: str) -> object | None:
    for name in names:
        symbol = getattr(module, name, None)
        if symbol is not None:
            return symbol
    return None


try:
    from PySide6 import Qt3DCore, Qt3DExtras, Qt3DRender

    QEntity = _resolve_symbol(Qt3DCore, "QEntity", "Qt3DCore.QEntity")
    QTransform = _resolve_symbol(Qt3DCore, "QTransform", "Qt3DCore.QTransform")

    Qt3DWindow = _resolve_symbol(Qt3DExtras, "Qt3DWindow", "Qt3DExtras.Qt3DWindow")
    QPhongMaterial = _resolve_symbol(Qt3DExtras, "QPhongMaterial", "Qt3DExtras.QPhongMaterial")
    QPhongAlphaMaterial = _resolve_optional_symbol(
        Qt3DExtras,
        "QPhongAlphaMaterial",
        "Qt3DExtras.QPhongAlphaMaterial",
    )
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
        self._timer = QTimer(self)
        self._alpha_material_class = QPhongAlphaMaterial if QT3D_AVAILABLE else None

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
        yaw = 0.0 if self._mode == "neutral" else ACTIVE_ASSET_CATALOG.pose_yaw_for_mode(self._mode)
        idle_turn = 1.1 * math.sin(self._pulse * 0.42)
        for entry in self._layer_entities:
            transform = entry["transform"]
            spec: LayerAssetSpec = entry["spec"]
            transform.setScale(spec.base_scale * breath)
            transform.setRotationY(yaw + idle_turn)

    def _setup_camera(self, view3d: object) -> None:
        camera = view3d.camera()
        camera.lens().setPerspectiveProjection(33.0, 1.0, 0.1, 1000.0)

        if self._mode == "skeleton":
            camera.setPosition(QVector3D(0.0, 1.03, 3.28))
        elif self._mode == "fat":
            camera.setPosition(QVector3D(0.48, 1.04, 3.28))
        elif self._mode == "muscle":
            camera.setPosition(QVector3D(2.72, 1.02, 0.0))
        else:
            camera.setPosition(QVector3D(0.14, 1.03, 3.28))

        camera.setViewCenter(QVector3D(0.0, 0.60, 0.0))

    def _setup_lights(self) -> None:
        light = QEntity(self._root_entity)
        point = QPointLight(light)
        point.setColor(QColor(220, 244, 255))
        point.setIntensity(2.0)
        t = QTransform(light)
        t.setTranslation(QVector3D(3.3, 4.6, 3.0))
        light.addComponent(point)
        light.addComponent(t)

        fill = QEntity(self._root_entity)
        fill_light = QPointLight(fill)
        fill_light.setColor(QColor(118, 170, 238))
        fill_light.setIntensity(1.2)
        fill_t = QTransform(fill)
        fill_t.setTranslation(QVector3D(-3.15, 2.1, 2.25))
        fill.addComponent(fill_light)
        fill.addComponent(fill_t)

        rim = QEntity(self._root_entity)
        rim_light = QPointLight(rim)
        rim_light.setColor(QColor(92, 154, 250))
        rim_light.setIntensity(0.78)
        rim_t = QTransform(rim)
        rim_t.setTranslation(QVector3D(-1.2, 2.1, -3.0))
        rim.addComponent(rim_light)
        rim.addComponent(rim_t)

    def _build_layer_entities(self) -> None:
        for spec in ACTIVE_ASSET_CATALOG.layer_specs():
            entity = QEntity(self._root_entity)

            transform = QTransform(entity)
            transform.setScale(spec.base_scale)
            transform.setTranslation(QVector3D(0.0, -0.05, 0.0))
            transform.setRotationY(ACTIVE_ASSET_CATALOG.pose_yaw_for_mode(self._mode))
            entity.addComponent(transform)

            model = self._build_layer_geometry(entity, spec.layer_index, QColor(*spec.rgb))

            self._layer_entities.append(
                {
                    "spec": spec,
                    "entity": entity,
                    "materials": model["materials"],
                    "parts": model["parts"],
                    "transform": transform,
                }
            )

    def _make_material(self, parent: object, color: QColor, opacity: float, shininess: float) -> object:
        opacity = max(0.02, min(0.98, opacity))
        if self._alpha_material_class is not None:
            material = self._alpha_material_class(parent)
            material.setDiffuse(color)
            if hasattr(material, "setAlpha"):
                material.setAlpha(opacity)
        else:
            material = QPhongMaterial(parent)
            diffuse = QColor(color)
            diffuse.setAlphaF(opacity)
            material.setDiffuse(diffuse)

        if hasattr(material, "setAmbient"):
            ambient = QColor(color).darker(136)
            ambient.setAlphaF(min(0.98, opacity))
            material.setAmbient(ambient)
        if hasattr(material, "setSpecular"):
            material.setSpecular(QColor(208, 235, 255))
        if hasattr(material, "setShininess"):
            material.setShininess(shininess)
        return material

    def _build_material_entry(
        self,
        parent: object,
        color: QColor,
        opacity: float,
        shininess: float,
    ) -> MaterialEntry:
        return {
            "material": self._make_material(parent, color, opacity, shininess),
            "base_color": QColor(color),
            "base_opacity": float(opacity),
        }

    def _set_material_style(self, material_entry: MaterialEntry, color: QColor, opacity: float) -> None:
        material = material_entry["material"]
        opacity = max(0.02, min(0.98, float(opacity)))

        diffuse = QColor(color)
        diffuse.setAlphaF(opacity)
        material.setDiffuse(diffuse)

        if hasattr(material, "setAlpha"):
            material.setAlpha(opacity)
        if hasattr(material, "setAmbient"):
            ambient = QColor(color).darker(136)
            ambient.setAlphaF(opacity)
            material.setAmbient(ambient)

    def _add_box_part(
        self,
        parent: object,
        color: QColor,
        opacity: float,
        x_extent: float,
        y_extent: float,
        z_extent: float,
        position: QVector3D,
        shininess: float = 26.0,
    ) -> dict[str, object]:
        part = QEntity(parent)
        mesh = QCuboidMesh(part)
        mesh.setXExtent(x_extent)
        mesh.setYExtent(y_extent)
        mesh.setZExtent(z_extent)

        material_entry = self._build_material_entry(part, color, opacity, shininess)

        transform = QTransform(part)
        transform.setTranslation(position)

        part.addComponent(mesh)
        part.addComponent(material_entry["material"])
        part.addComponent(transform)
        return {
            "entity": part,
            "mesh": mesh,
            "material_entry": material_entry,
            "transform": transform,
        }

    def _add_cylinder_part(
        self,
        parent: object,
        color: QColor,
        opacity: float,
        radius: float,
        length: float,
        position: QVector3D,
        rot_x: float = 0.0,
        rot_y: float = 0.0,
        rot_z: float = 0.0,
        shininess: float = 28.0,
    ) -> dict[str, object]:
        part = QEntity(parent)
        mesh = QCylinderMesh(part)
        mesh.setRadius(radius)
        mesh.setLength(length)
        mesh.setRings(28)
        mesh.setSlices(28)

        material_entry = self._build_material_entry(part, color, opacity, shininess)

        transform = QTransform(part)
        transform.setTranslation(position)
        if rot_x and hasattr(transform, "setRotationX"):
            transform.setRotationX(rot_x)
        if rot_y and hasattr(transform, "setRotationY"):
            transform.setRotationY(rot_y)
        if rot_z and hasattr(transform, "setRotationZ"):
            transform.setRotationZ(rot_z)

        part.addComponent(mesh)
        part.addComponent(material_entry["material"])
        part.addComponent(transform)
        return {
            "entity": part,
            "mesh": mesh,
            "material_entry": material_entry,
            "transform": transform,
        }

    def _add_sphere_part(
        self,
        parent: object,
        color: QColor,
        opacity: float,
        radius: float,
        position: QVector3D,
        scale: QVector3D | None = None,
        shininess: float = 30.0,
    ) -> dict[str, object]:
        part = QEntity(parent)
        mesh = QSphereMesh(part)
        mesh.setRadius(radius)
        if hasattr(mesh, "setRings"):
            mesh.setRings(32)
        if hasattr(mesh, "setSlices"):
            mesh.setSlices(32)

        material_entry = self._build_material_entry(part, color, opacity, shininess)

        transform = QTransform(part)
        transform.setTranslation(position)
        if scale is not None:
            if hasattr(transform, "setScale3D"):
                transform.setScale3D(scale)
            else:
                transform.setScale(max(scale.x(), scale.y(), scale.z()))

        part.addComponent(mesh)
        part.addComponent(material_entry["material"])
        part.addComponent(transform)
        return {
            "entity": part,
            "mesh": mesh,
            "material_entry": material_entry,
            "transform": transform,
        }

    def _build_layer_geometry(self, parent: object, layer_index: int, layer_color: QColor) -> dict[str, list[object]]:
        if layer_index <= 2:
            fullness = {0: 1.0, 1: 0.965, 2: 0.93}[layer_index]
            shell_opacity = {0: 0.14, 1: 0.20, 2: 0.28}[layer_index]
            shell_color = QColor(layer_color)
            parts = self._build_organic_shell(parent, shell_color, fullness, shell_opacity)
        elif layer_index == 3:
            parts = self._build_skeleton_core(parent, QColor(208, 236, 255), 0.72)
        elif layer_index == 4:
            parts = self._build_organ_core(parent)
        else:
            parts = self._build_vascular_core(parent)

        return {
            "parts": parts,
            "materials": [part["material_entry"] for part in parts],
        }

    def _build_organic_shell(
        self,
        parent: object,
        shell_color: QColor,
        fullness: float,
        opacity: float,
    ) -> list[PartEntry]:
        parts: list[PartEntry] = []
        core = QColor(shell_color)
        soft = shell_color.lighter(106)
        lower = shell_color.darker(112)

        shoulder_x = 0.24 * fullness
        arm_x = 0.33 * fullness
        hip_x = 0.125 * fullness

        parts.append(
            self._add_sphere_part(
                parent,
                soft,
                opacity * 0.95,
                0.16 * fullness,
                QVector3D(0.0, 1.67, 0.0),
                scale=QVector3D(0.86, 1.04, 0.88),
            )
        )
        parts.append(
            self._add_cylinder_part(parent, core, opacity * 0.95, 0.045 * fullness, 0.14, QVector3D(0.0, 1.47, 0.0))
        )

        parts.append(
            self._add_sphere_part(
                parent,
                core,
                opacity,
                0.255 * fullness,
                QVector3D(0.0, 1.12, 0.0),
                scale=QVector3D(1.04, 1.24, 0.72),
            )
        )
        parts.append(
            self._add_sphere_part(
                parent,
                core,
                opacity,
                0.215 * fullness,
                QVector3D(0.0, 0.80, 0.0),
                scale=QVector3D(0.96, 1.02, 0.70),
            )
        )
        parts.append(
            self._add_sphere_part(
                parent,
                lower,
                opacity,
                0.205 * fullness,
                QVector3D(0.0, 0.55, 0.0),
                scale=QVector3D(1.06, 0.80, 0.86),
            )
        )

        parts.append(self._add_sphere_part(parent, soft, opacity * 0.92, 0.07 * fullness, QVector3D(-shoulder_x, 1.26, 0.0)))
        parts.append(self._add_sphere_part(parent, soft, opacity * 0.92, 0.07 * fullness, QVector3D(shoulder_x, 1.26, 0.0)))

        parts.append(
            self._add_cylinder_part(
                parent,
                core,
                opacity * 0.94,
                0.066 * fullness,
                0.43,
                QVector3D(-arm_x, 0.99, 0.0),
                rot_z=11.0,
            )
        )
        parts.append(
            self._add_cylinder_part(
                parent,
                core,
                opacity * 0.94,
                0.066 * fullness,
                0.43,
                QVector3D(arm_x, 0.99, 0.0),
                rot_z=-11.0,
            )
        )
        parts.append(
            self._add_cylinder_part(
                parent,
                core,
                opacity * 0.94,
                0.056 * fullness,
                0.37,
                QVector3D(-0.39 * fullness, 0.56, 0.0),
                rot_z=6.0,
            )
        )
        parts.append(
            self._add_cylinder_part(
                parent,
                core,
                opacity * 0.94,
                0.056 * fullness,
                0.37,
                QVector3D(0.39 * fullness, 0.56, 0.0),
                rot_z=-6.0,
            )
        )
        parts.append(
            self._add_sphere_part(
                parent,
                lower,
                opacity * 0.94,
                0.047 * fullness,
                QVector3D(-0.405 * fullness, 0.30, 0.05),
                scale=QVector3D(1.2, 0.5, 1.55),
            )
        )
        parts.append(
            self._add_sphere_part(
                parent,
                lower,
                opacity * 0.94,
                0.047 * fullness,
                QVector3D(0.405 * fullness, 0.30, 0.05),
                scale=QVector3D(1.2, 0.5, 1.55),
            )
        )

        parts.append(self._add_cylinder_part(parent, core, opacity * 0.96, 0.096 * fullness, 0.54, QVector3D(-hip_x, 0.18, 0.0)))
        parts.append(self._add_cylinder_part(parent, core, opacity * 0.96, 0.096 * fullness, 0.54, QVector3D(hip_x, 0.18, 0.0)))
        parts.append(self._add_cylinder_part(parent, core, opacity * 0.96, 0.078 * fullness, 0.52, QVector3D(-hip_x, -0.36, 0.0)))
        parts.append(self._add_cylinder_part(parent, core, opacity * 0.96, 0.078 * fullness, 0.52, QVector3D(hip_x, -0.36, 0.0)))
        parts.append(
            self._add_sphere_part(
                parent,
                lower,
                opacity,
                0.062 * fullness,
                QVector3D(-hip_x, -0.64, 0.08),
                scale=QVector3D(1.28, 0.36, 2.1),
            )
        )
        parts.append(
            self._add_sphere_part(
                parent,
                lower,
                opacity,
                0.062 * fullness,
                QVector3D(hip_x, -0.64, 0.08),
                scale=QVector3D(1.28, 0.36, 2.1),
            )
        )

        return parts

    def _build_skeleton_core(self, parent: object, bone_color: QColor, opacity: float) -> list[PartEntry]:
        parts: list[PartEntry] = []
        spine_color = bone_color.lighter(104)

        parts.append(
            self._add_sphere_part(
                parent,
                bone_color,
                opacity,
                0.145,
                QVector3D(0.0, 1.70, 0.0),
                scale=QVector3D(0.9, 1.05, 0.9),
            )
        )
        parts.append(self._add_cylinder_part(parent, bone_color, opacity, 0.052, 0.14, QVector3D(0.0, 1.50, 0.0)))
        parts.append(self._add_cylinder_part(parent, bone_color, opacity, 0.125, 0.58, QVector3D(0.0, 1.07, 0.0)))
        parts.append(self._add_sphere_part(parent, bone_color, opacity, 0.16, QVector3D(0.0, 0.56, 0.0), scale=QVector3D(1.05, 0.62, 0.82)))

        for index in range(9):
            y = 1.36 - (index * 0.105)
            parts.append(self._add_sphere_part(parent, spine_color, opacity, 0.045, QVector3D(0.0, y, -0.01)))

        for side in (-1.0, 1.0):
            x = 0.35 * side
            parts.append(self._add_cylinder_part(parent, bone_color, opacity, 0.04, 0.43, QVector3D(x, 1.0, 0.0), rot_z=-10.0 * side))
            parts.append(self._add_cylinder_part(parent, bone_color, opacity, 0.035, 0.38, QVector3D(0.39 * side, 0.50, 0.0), rot_z=-6.0 * side))
            parts.append(self._add_cylinder_part(parent, bone_color, opacity, 0.052, 0.50, QVector3D(0.145 * side, 0.23, 0.0)))
            parts.append(self._add_cylinder_part(parent, bone_color, opacity, 0.046, 0.48, QVector3D(0.145 * side, -0.31, 0.0)))

        return parts

    def _build_organ_core(self, parent: object) -> list[PartEntry]:
        parts: list[PartEntry] = []

        heart = QColor(235, 106, 128)
        lung = QColor(126, 196, 255)
        spine = QColor(168, 130, 255)

        parts.append(
            self._add_sphere_part(
                parent,
                spine,
                0.78,
                0.055,
                QVector3D(0.0, 0.98, -0.03),
                scale=QVector3D(0.65, 3.55, 0.65),
                shininess=20.0,
            )
        )
        parts.append(
            self._add_sphere_part(
                parent,
                heart,
                0.9,
                0.11,
                QVector3D(0.03, 1.00, 0.10),
                scale=QVector3D(0.9, 1.08, 0.8),
                shininess=35.0,
            )
        )
        parts.append(
            self._add_sphere_part(
                parent,
                lung,
                0.66,
                0.12,
                QVector3D(-0.12, 1.06, 0.03),
                scale=QVector3D(0.95, 1.25, 0.75),
                shininess=18.0,
            )
        )
        parts.append(
            self._add_sphere_part(
                parent,
                lung,
                0.66,
                0.12,
                QVector3D(0.15, 1.06, 0.03),
                scale=QVector3D(0.95, 1.25, 0.75),
                shininess=18.0,
            )
        )

        parts.append(self._add_cylinder_part(parent, heart, 0.9, 0.022, 0.22, QVector3D(0.01, 1.21, 0.08), shininess=34.0))
        parts.append(self._add_cylinder_part(parent, heart, 0.9, 0.02, 0.15, QVector3D(0.09, 0.88, 0.09), rot_z=-16.0, shininess=34.0))

        return parts

    def _build_vascular_core(self, parent: object) -> list[PartEntry]:
        parts: list[PartEntry] = []
        artery = QColor(182, 98, 242)
        vein = QColor(96, 180, 255)

        parts.append(self._add_cylinder_part(parent, artery, 0.92, 0.018, 0.82, QVector3D(0.0, 0.95, 0.10), shininess=18.0))
        parts.append(self._add_cylinder_part(parent, artery, 0.9, 0.013, 0.30, QVector3D(0.0, 1.40, 0.10), shininess=18.0))

        for side in (-1.0, 1.0):
            parts.append(
                self._add_cylinder_part(
                    parent,
                    vein,
                    0.85,
                    0.012,
                    0.56,
                    QVector3D(0.34 * side, 0.92, 0.09),
                    rot_z=-12.0 * side,
                    shininess=14.0,
                )
            )
            parts.append(
                self._add_cylinder_part(
                    parent,
                    vein,
                    0.85,
                    0.010,
                    0.46,
                    QVector3D(0.38 * side, 0.48, 0.08),
                    rot_z=-6.0 * side,
                    shininess=14.0,
                )
            )
            parts.append(
                self._add_cylinder_part(
                    parent,
                    artery,
                    0.88,
                    0.013,
                    0.62,
                    QVector3D(0.14 * side, 0.20, 0.08),
                    shininess=16.0,
                )
            )
            parts.append(
                self._add_cylinder_part(
                    parent,
                    artery,
                    0.88,
                    0.011,
                    0.56,
                    QVector3D(0.14 * side, -0.33, 0.08),
                    shininess=16.0,
                )
            )

        return parts

    def _refresh_layers(self) -> None:
        if self._mode == "neutral":
            focus = self._active_layer
        else:
            focus = ACTIVE_ASSET_CATALOG.focus_layer_for_mode(self._mode)

        for entry in self._layer_entities:
            spec: LayerAssetSpec = entry["spec"]
            entity = entry["entity"]
            materials = entry["materials"]

            visible = spec.layer_index <= self._active_layer
            entity.setEnabled(visible)
            if not visible:
                continue

            emphasis_opacity = 1.0
            tone = "inactive"
            if spec.layer_index == self._active_layer:
                tone = "active"
                emphasis_opacity = 1.06
            elif spec.layer_index == focus:
                tone = "focus"
                emphasis_opacity = 1.0
            else:
                tone = "inactive"
                emphasis_opacity = 0.78

            for material_entry in materials:
                base_color = QColor(material_entry["base_color"])
                base_opacity = float(material_entry["base_opacity"])

                if tone == "active":
                    color = base_color.lighter(108)
                elif tone == "focus":
                    color = base_color.lighter(102)
                else:
                    color = base_color.darker(104)

                self._set_material_style(material_entry, color, base_opacity * emphasis_opacity)
