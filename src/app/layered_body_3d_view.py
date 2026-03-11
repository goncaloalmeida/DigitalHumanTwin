from __future__ import annotations

from typing import Optional

from PySide6.QtGui import QColor, QVector3D
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

try:
    from PySide6.Qt3DCore import QEntity, QTransform
    from PySide6.Qt3DExtras import (
        QCuboidMesh,
        QOrbitCameraController,
        QPhongMaterial,
        QSphereMesh,
        Qt3DWindow,
    )
    from PySide6.Qt3DRender import QPointLight

    QT3D_AVAILABLE = True
except ImportError:
    QT3D_AVAILABLE = False


class LayeredBody3DView(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._root_entity: Optional[QEntity] = None
        self._layer_entities: list[QEntity] = []

        layout = QVBoxLayout(self)

        if not QT3D_AVAILABLE:
            layout.addWidget(
                QLabel(
                    "Qt3D nao esta disponivel nesta instalacao do PySide6.",
                    self,
                )
            )
            return

        view3d = Qt3DWindow()
        container = QWidget.createWindowContainer(view3d, self)
        container.setMinimumHeight(420)
        layout.addWidget(container)

        self._root_entity = QEntity()
        view3d.setRootEntity(self._root_entity)

        camera = view3d.camera()
        camera.lens().setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 1000.0)
        camera.setPosition(QVector3D(0.0, 2.5, 14.0))
        camera.setViewCenter(QVector3D(0.0, 0.0, 0.0))

        camera_controller = QOrbitCameraController(self._root_entity)
        camera_controller.setCamera(camera)
        camera_controller.setLinearSpeed(75.0)
        camera_controller.setLookSpeed(180.0)

        light_entity = QEntity(self._root_entity)
        point_light = QPointLight(light_entity)
        point_light.setColor(QColor(255, 255, 255))
        point_light.setIntensity(1.25)
        light_transform = QTransform(light_entity)
        light_transform.setTranslation(QVector3D(8.0, 10.0, 12.0))
        light_entity.addComponent(point_light)
        light_entity.addComponent(light_transform)

        self._build_layers()

    def set_visible_layer(self, layer_index: int) -> None:
        if not QT3D_AVAILABLE:
            return

        for index, entity in enumerate(self._layer_entities):
            entity.setEnabled(index <= layer_index)

    def _build_layers(self) -> None:
        if self._root_entity is None:
            return

        self._layer_entities = [
            self._make_sphere_layer(3.2, QColor(247, 193, 168, 180), QVector3D(0.0, 0.0, 0.0)),
            self._make_sphere_layer(2.9, QColor(242, 196, 142, 165), QVector3D(0.0, -0.05, 0.0)),
            self._make_sphere_layer(2.45, QColor(198, 72, 72, 220), QVector3D(0.0, -0.1, 0.0)),
            self._make_sphere_layer(2.0, QColor(236, 232, 219, 220), QVector3D(0.0, -0.1, 0.0)),
            self._make_sphere_layer(1.35, QColor(121, 159, 187, 225), QVector3D(0.0, -0.05, 0.0)),
            self._make_heart_layer(),
        ]

        self.set_visible_layer(0)

    def _make_sphere_layer(
        self,
        radius: float,
        color: QColor,
        translation: QVector3D,
    ) -> QEntity:
        if self._root_entity is None:
            return QEntity()

        entity = QEntity(self._root_entity)
        mesh = QSphereMesh(entity)
        mesh.setRadius(radius)

        material = QPhongMaterial(entity)
        material.setDiffuse(color)

        transform = QTransform(entity)
        transform.setTranslation(translation)

        entity.addComponent(mesh)
        entity.addComponent(material)
        entity.addComponent(transform)
        return entity

    def _make_heart_layer(self) -> QEntity:
        if self._root_entity is None:
            return QEntity()

        group = QEntity(self._root_entity)

        heart = QEntity(group)
        heart_mesh = QSphereMesh(heart)
        heart_mesh.setRadius(0.72)
        heart_material = QPhongMaterial(heart)
        heart_material.setDiffuse(QColor(172, 24, 38, 255))
        heart_transform = QTransform(heart)
        heart_transform.setTranslation(QVector3D(0.25, -0.15, 0.1))
        heart_transform.setScale3D(QVector3D(1.0, 1.2, 0.9))
        heart.addComponent(heart_mesh)
        heart.addComponent(heart_material)
        heart.addComponent(heart_transform)

        artery = QEntity(group)
        artery_mesh = QCuboidMesh(artery)
        artery_mesh.setXExtent(0.2)
        artery_mesh.setYExtent(1.2)
        artery_mesh.setZExtent(0.2)
        artery_material = QPhongMaterial(artery)
        artery_material.setDiffuse(QColor(208, 56, 56, 255))
        artery_transform = QTransform(artery)
        artery_transform.setTranslation(QVector3D(0.25, 0.9, 0.1))
        artery.addComponent(artery_mesh)
        artery.addComponent(artery_material)
        artery.addComponent(artery_transform)

        return group