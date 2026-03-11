from __future__ import annotations

from math import sin
from typing import Literal

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import (
    QColor,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPainterPathStroker,
    QPen,
    QRadialGradient,
)
from PySide6.QtWidgets import QWidget

BodyMode = Literal["skeleton", "fat", "muscle"]
PoseMode = Literal["front", "three_quarter", "side"]


class BodyPreviewWidget(QWidget):
    def __init__(self, mode: BodyMode, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._mode = mode
        self._active_layer = 0
        self._phase = 0.0
        self.setMinimumSize(220, 360)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(35)

    def set_active_layer(self, layer_index: int) -> None:
        self._active_layer = layer_index
        self.update()

    def _tick(self) -> None:
        self._phase += 0.055
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self._draw_background(painter)
        self._draw_scanlines(painter)

        s = min(self.width() / 260.0, self.height() / 410.0)
        cx = self.width() * 0.5
        top_y = self.height() * 0.02
        pulse = 0.5 + 0.5 * sin(self._phase)

        pose = self._pose_for_mode()
        lean = {"front": 0.0, "three_quarter": 5.5, "side": 8.0}[pose] * s

        body = self._build_body_path(cx, top_y, s, pose, lean, pulse)

        self._draw_ground_shadow(painter, cx, top_y, s)
        self._draw_body_shell(painter, body, cx, top_y, s, pulse)
        self._draw_layer_content(painter, cx, top_y, s, pose, lean, pulse)
        self._draw_outer_glow(painter, body, s)

        painter.end()

    def _pose_for_mode(self) -> PoseMode:
        if self._mode == "skeleton":
            return "front"
        if self._mode == "fat":
            return "three_quarter"
        return "side"

    def _draw_background(self, painter: QPainter) -> None:
        g = QLinearGradient(0.0, 0.0, 0.0, float(self.height()))
        g.setColorAt(0.0, QColor("#133f8a"))
        g.setColorAt(0.45, QColor("#0f2f6c"))
        g.setColorAt(1.0, QColor("#072255"))
        painter.fillRect(self.rect(), g)

        vignette = QRadialGradient(
            QPointF(self.width() * 0.5, self.height() * 0.52),
            max(self.width(), self.height()) * 0.7,
        )
        vignette.setColorAt(0.0, QColor(0, 0, 0, 0))
        vignette.setColorAt(1.0, QColor(0, 0, 0, 85))
        painter.fillRect(self.rect(), vignette)

    def _draw_scanlines(self, painter: QPainter) -> None:
        painter.setPen(QPen(QColor(140, 194, 255, 15), 1.0))
        for y in range(0, self.height(), 6):
            painter.drawLine(0, y, self.width(), y)

    def _draw_ground_shadow(self, painter: QPainter, cx: float, top_y: float, s: float) -> None:
        shadow = QRadialGradient(QPointF(cx, top_y + 388 * s), 64 * s)
        shadow.setColorAt(0.0, QColor(0, 0, 0, 110))
        shadow.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(shadow)
        painter.drawEllipse(QRectF(cx - 72 * s, top_y + 366 * s, 144 * s, 44 * s))

    def _build_body_path(
        self,
        cx: float,
        top_y: float,
        s: float,
        pose: PoseMode,
        lean: float,
        pulse: float,
    ) -> QPainterPath:
        chest_scale = 1.0 + pulse * 0.028
        shoulder_scale = {"front": 1.0, "three_quarter": 1.07, "side": 0.64}[pose]
        hip_scale = {"front": 1.0, "three_quarter": 1.06, "side": 0.74}[pose]

        neck_y = top_y + 58 * s
        chest_y = top_y + 108 * s
        hip_y = top_y + 206 * s
        knee_y = top_y + 304 * s
        foot_y = top_y + 372 * s

        shoulder_x = 56 * s * shoulder_scale * chest_scale
        hip_x = 43 * s * hip_scale

        path = QPainterPath(QPointF(cx - 15 * s + lean, neck_y))

        path.cubicTo(
            cx - shoulder_x + lean,
            top_y + 70 * s,
            cx - (shoulder_x + 10 * s) + lean,
            chest_y,
            cx - hip_x + lean,
            top_y + 174 * s,
        )
        path.cubicTo(
            cx - (hip_x - 6 * s) + lean,
            hip_y,
            cx - (hip_x - 9 * s) + lean,
            top_y + 252 * s,
            cx - (hip_x - 6 * s) + lean,
            knee_y,
        )
        path.cubicTo(
            cx - (hip_x - 3 * s) + lean,
            top_y + 332 * s,
            cx - (hip_x + 7 * s) + lean,
            top_y + 352 * s,
            cx - (hip_x + 11 * s) + lean,
            foot_y,
        )
        path.lineTo(QPointF(cx - 8 * s + lean, foot_y))
        path.cubicTo(
            cx - 8 * s + lean,
            top_y + 338 * s,
            cx - 5 * s + lean,
            top_y + 292 * s,
            cx - 2 * s + lean,
            top_y + 242 * s,
        )
        path.cubicTo(
            cx + 1 * s + lean,
            top_y + 221 * s,
            cx + 1 * s + lean,
            top_y + 205 * s,
            cx + 2 * s + lean,
            hip_y,
        )
        path.cubicTo(
            cx + 4 * s + lean,
            top_y + 205 * s,
            cx + 4 * s + lean,
            top_y + 221 * s,
            cx + 7 * s + lean,
            top_y + 242 * s,
        )
        path.cubicTo(
            cx + 10 * s + lean,
            top_y + 292 * s,
            cx + 13 * s + lean,
            top_y + 338 * s,
            cx + 13 * s + lean,
            foot_y,
        )
        path.lineTo(QPointF(cx + hip_x + lean, foot_y))
        path.cubicTo(
            cx + (hip_x - 4 * s) + lean,
            top_y + 351 * s,
            cx + (hip_x - 1 * s) + lean,
            top_y + 333 * s,
            cx + (hip_x - 3 * s) + lean,
            knee_y,
        )
        path.cubicTo(
            cx + (hip_x - 5 * s) + lean,
            top_y + 252 * s,
            cx + (hip_x - 3 * s) + lean,
            hip_y,
            cx + hip_x + lean,
            top_y + 174 * s,
        )
        path.cubicTo(
            cx + (shoulder_x + 12 * s) + lean,
            chest_y,
            cx + shoulder_x + lean,
            top_y + 70 * s,
            cx + 18 * s + lean,
            neck_y,
        )
        path.closeSubpath()
        return path

    def _draw_body_shell(
        self,
        painter: QPainter,
        body: QPainterPath,
        cx: float,
        top_y: float,
        s: float,
        pulse: float,
    ) -> None:
        body_grad = QLinearGradient(cx, top_y + 56 * s, cx, top_y + 374 * s)
        body_grad.setColorAt(0.0, QColor("#6ea8f0"))
        body_grad.setColorAt(0.35, QColor("#4d81cb"))
        body_grad.setColorAt(1.0, QColor("#255aa5"))

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(body_grad)
        painter.drawPath(body)

        head_rect = QRectF(cx - 20 * s, top_y + 10 * s, 40 * s, 44 * s)
        head_glow = QRadialGradient(head_rect.center(), 26 * s)
        head_glow.setColorAt(0.0, QColor(149, 210, 255, int(165 + 35 * pulse)))
        head_glow.setColorAt(1.0, QColor(65, 121, 195, 0))
        painter.setBrush(head_glow)
        painter.drawEllipse(head_rect.adjusted(-4 * s, -4 * s, 4 * s, 4 * s))

        painter.setBrush(QColor(174, 223, 255, 40))
        painter.drawPath(body)

        painter.setPen(QPen(QColor(185, 231, 255, 72), 1.4 * s))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(body)

    def _draw_layer_content(
        self,
        painter: QPainter,
        cx: float,
        top_y: float,
        s: float,
        pose: PoseMode,
        lean: float,
        pulse: float,
    ) -> None:
        self._draw_fat(painter, cx, top_y, s, pose, lean, pulse)
        self._draw_muscle(painter, cx, top_y, s, pose, lean, pulse)
        self._draw_skeleton(painter, cx, top_y, s, pose, lean, pulse)

    def _draw_fat(
        self,
        painter: QPainter,
        cx: float,
        top_y: float,
        s: float,
        pose: PoseMode,
        lean: float,
        pulse: float,
    ) -> None:
        strength = 1.0 if self._active_layer >= 1 else 0.2
        if self._mode == "fat":
            strength = min(1.0, strength + 0.36)

        alpha = int((168 + 32 * pulse) * strength)
        width_boost = {"front": 1.0, "three_quarter": 1.09, "side": 0.78}[pose]

        painter.setPen(Qt.PenStyle.NoPen)

        core = QRadialGradient(QPointF(cx + lean, top_y + 176 * s), 76 * s)
        core.setColorAt(0.0, QColor(203, 236, 255, alpha))
        core.setColorAt(1.0, QColor(172, 212, 243, int(alpha * 0.24)))
        painter.setBrush(core)
        painter.drawEllipse(
            QRectF(
                cx - 58 * s * width_boost + lean,
                top_y + 102 * s,
                116 * s * width_boost,
                162 * s,
            )
        )

        painter.setBrush(QColor(190, 229, 255, int(alpha * 0.48)))
        painter.drawEllipse(QRectF(cx - 28 * s + lean, top_y + 228 * s, 40 * s, 88 * s))
        painter.drawEllipse(QRectF(cx + 4 * s + lean, top_y + 228 * s, 40 * s, 88 * s))

    def _draw_muscle(
        self,
        painter: QPainter,
        cx: float,
        top_y: float,
        s: float,
        pose: PoseMode,
        lean: float,
        pulse: float,
    ) -> None:
        strength = 1.0 if self._active_layer >= 2 else 0.2
        if self._mode == "muscle":
            strength = min(1.0, strength + 0.36)

        alpha = int((206 + 42 * pulse) * strength)
        muscle = QColor(129, 221, 255, alpha)

        painter.setPen(QPen(muscle, 2.2 * s, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.setBrush(Qt.BrushStyle.NoBrush)

        chest = QPainterPath()
        chest.moveTo(cx - 31 * s + lean, top_y + 100 * s)
        chest.cubicTo(
            QPointF(cx - 12 * s + lean, top_y + 78 * s),
            QPointF(cx + 12 * s + lean, top_y + 78 * s),
            QPointF(cx + 30 * s + lean, top_y + 100 * s),
        )
        chest.cubicTo(
            QPointF(cx + 10 * s + lean, top_y + 126 * s),
            QPointF(cx - 10 * s + lean, top_y + 126 * s),
            QPointF(cx - 31 * s + lean, top_y + 100 * s),
        )
        painter.drawPath(chest)

        center = QPainterPath(QPointF(cx + lean, top_y + 118 * s))
        center.cubicTo(
            QPointF(cx - 1 * s + lean, top_y + 151 * s),
            QPointF(cx + 2 * s + lean, top_y + 180 * s),
            QPointF(cx + lean, top_y + 214 * s),
        )
        painter.drawPath(center)

        for offset in (-17, -9, 9, 17):
            painter.drawLine(
                QPointF(cx + offset * s + lean, top_y + 128 * s),
                QPointF(cx + (offset * 0.8) * s + lean, top_y + 214 * s),
            )

        limb_vis = 0.65 if pose == "side" else 1.0
        if limb_vis > 0.7:
            self._draw_muscle_limb(painter, cx, top_y, s, lean, left=True)
        self._draw_muscle_limb(painter, cx, top_y, s, lean, left=False)

        painter.drawLine(QPointF(cx - 11 * s + lean, top_y + 218 * s), QPointF(cx - 15 * s + lean, top_y + 344 * s))
        painter.drawLine(QPointF(cx + 11 * s + lean, top_y + 218 * s), QPointF(cx + 15 * s + lean, top_y + 344 * s))

    def _draw_muscle_limb(self, painter: QPainter, cx: float, top_y: float, s: float, lean: float, left: bool) -> None:
        d = -1.0 if left else 1.0
        painter.drawLine(
            QPointF(cx + d * 35 * s + lean, top_y + 97 * s),
            QPointF(cx + d * 57 * s + lean, top_y + 178 * s),
        )
        painter.drawLine(
            QPointF(cx + d * 57 * s + lean, top_y + 178 * s),
            QPointF(cx + d * 49 * s + lean, top_y + 266 * s),
        )

    def _draw_skeleton(
        self,
        painter: QPainter,
        cx: float,
        top_y: float,
        s: float,
        pose: PoseMode,
        lean: float,
        pulse: float,
    ) -> None:
        strength = 1.0 if self._active_layer >= 3 else 0.25
        if self._mode == "skeleton":
            strength = min(1.0, strength + 0.34)

        alpha = int((205 + 35 * pulse) * strength)
        bone = QColor(214, 240, 255, alpha)

        painter.setPen(QPen(bone, 2.7 * s, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.setBrush(Qt.BrushStyle.NoBrush)

        skull = QRectF(cx - 12 * s + lean, top_y + 14 * s, 24 * s, 28 * s)
        painter.drawEllipse(skull)
        painter.drawArc(skull.adjusted(3 * s, 13 * s, -3 * s, 5 * s), 0, 180 * 16)

        spine = QPainterPath(QPointF(cx + lean, top_y + 64 * s))
        spine.cubicTo(
            QPointF(cx - 2 * s + lean, top_y + 112 * s),
            QPointF(cx + 3 * s + lean, top_y + 158 * s),
            QPointF(cx + 1 * s + lean, top_y + 218 * s),
        )
        painter.drawPath(spine)

        for i in range(7):
            y = top_y + (74 + i * 20) * s
            painter.drawEllipse(QPointF(cx + lean, y), 2.3 * s, 1.5 * s)

        rib_rect = QRectF(cx - 33 * s + lean, top_y + 84 * s, 66 * s, 76 * s)
        for i in range(5):
            inset = i * 5.3 * s
            painter.drawArc(rib_rect.adjusted(inset, inset, -inset, -inset), 25 * 16, 130 * 16)

        clavicle = QPainterPath(QPointF(cx - 25 * s + lean, top_y + 77 * s))
        clavicle.quadTo(QPointF(cx + lean, top_y + 66 * s), QPointF(cx + 26 * s + lean, top_y + 77 * s))
        painter.drawPath(clavicle)

        pelvis = QPainterPath()
        pelvis.moveTo(cx - 23 * s + lean, top_y + 186 * s)
        pelvis.cubicTo(
            QPointF(cx - 35 * s + lean, top_y + 197 * s),
            QPointF(cx - 26 * s + lean, top_y + 214 * s),
            QPointF(cx - 6 * s + lean, top_y + 214 * s),
        )
        pelvis.lineTo(QPointF(cx + 8 * s + lean, top_y + 214 * s))
        pelvis.cubicTo(
            QPointF(cx + 27 * s + lean, top_y + 214 * s),
            QPointF(cx + 36 * s + lean, top_y + 197 * s),
            QPointF(cx + 23 * s + lean, top_y + 186 * s),
        )
        painter.drawPath(pelvis)

        arm_vis = 0.6 if pose == "side" else 1.0
        if arm_vis > 0.7:
            self._draw_bone_limb(painter, cx, top_y, s, lean, left=True)
        self._draw_bone_limb(painter, cx, top_y, s, lean, left=False)

        painter.drawLine(QPointF(cx - 8 * s + lean, top_y + 215 * s), QPointF(cx - 14 * s + lean, top_y + 351 * s))
        painter.drawLine(QPointF(cx + 8 * s + lean, top_y + 215 * s), QPointF(cx + 14 * s + lean, top_y + 351 * s))

    def _draw_bone_limb(self, painter: QPainter, cx: float, top_y: float, s: float, lean: float, left: bool) -> None:
        d = -1.0 if left else 1.0
        shoulder = QPointF(cx + d * 35 * s + lean, top_y + 90 * s)
        elbow = QPointF(cx + d * 56 * s + lean, top_y + 177 * s)
        wrist = QPointF(cx + d * 48 * s + lean, top_y + 265 * s)

        painter.drawLine(shoulder, elbow)
        painter.drawLine(elbow, wrist)

        painter.setBrush(QColor(224, 244, 255, 210))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(shoulder, 3.2 * s, 3.2 * s)
        painter.drawEllipse(elbow, 3.6 * s, 3.6 * s)
        painter.drawEllipse(wrist, 3.0 * s, 3.0 * s)

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(214, 240, 255, 220), 2.7 * s, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))

    def _draw_outer_glow(self, painter: QPainter, body: QPainterPath, s: float) -> None:
        stroker = QPainterPathStroker()
        stroker.setWidth(8.5 * s)
        glow = stroker.createStroke(body)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(104, 178, 255, 30))
        painter.drawPath(glow)
