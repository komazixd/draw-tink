from PyQt6.QtWidgets import QWidget, QFileDialog
from PyQt6.QtGui import (
    QPainter, QPen, QColor, QPixmap, QPainterPath,
    QMouseEvent, QWheelEvent, QGuiApplication
)
from PyQt6.QtCore import Qt, QPointF, QRectF


class CanvasView(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600)
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(Qt.GlobalColor.white)

        self.pen_color = QColor("black")
        self.pen_size = 5
        self.drawing = False
        self.last_point = None
        self.tool = "pen"  # pen, eraser, shape, select, pan
        self.shape = None  # rectangle, ellipse, heart

        self.undo_stack = []
        self.redo_stack = []

        self.scale_factor = 1.0
        self.offset = QPointF(0, 0)

        self.panning = False
        self.pan_start_pos = QPointF()

        self.selection_rect = None
        self.selected_pixmap = None
        self.selection_offset = QPointF()
        self.dragging_selection = False

    def set_tool(self, tool_name):
        self.tool = tool_name
        self.selection_rect = None
        self.selected_pixmap = None
        self.update()

    def set_shape(self, shape_name):
        self.shape = shape_name
        self.set_tool("shape")

    def set_pen_color(self, color):
        self.pen_color = color

    def set_pen_size(self, size):
        self.pen_size = size

    def undo(self):
        if self.undo_stack:
            self.redo_stack.append(self.pixmap.copy())
            self.pixmap = self.undo_stack.pop()
            self.update()

    def redo(self):
        if self.redo_stack:
            self.undo_stack.append(self.pixmap.copy())
            self.pixmap = self.redo_stack.pop()
            self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self.map_to_canvas(event.position())
            if self.tool in ("pen", "eraser"):
                self.undo_stack.append(self.pixmap.copy())
                self.redo_stack.clear()
                self.drawing = True
                self.last_point = pos
            elif self.tool == "shape":
                self.undo_stack.append(self.pixmap.copy())
                self.redo_stack.clear()
                self.start_point = pos
                self.drawing = True
            elif self.tool == "select":
                if self.selection_rect and self.selection_rect.contains(pos):
                    self.dragging_selection = True
                    self.selection_offset = pos - self.selection_rect.topLeft()
                else:
                    self.selection_rect = QRectF(pos, pos)
                    self.selected_pixmap = None
                    self.drawing = True
            elif self.tool == "pan":
                self.panning = True
                self.pan_start_pos = event.position()
        elif event.button() == Qt.MouseButton.MiddleButton:
            self.panning = True
            self.pan_start_pos = event.position()

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = self.map_to_canvas(event.position())
        if self.drawing:
            if self.tool == "pen":
                painter = QPainter(self.pixmap)
                pen = QPen(self.pen_color, self.pen_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
                painter.setPen(pen)
                painter.drawLine(self.last_point, pos)
                self.last_point = pos
                self.update()
            elif self.tool == "eraser":
                painter = QPainter(self.pixmap)
                pen = QPen(Qt.GlobalColor.white, self.pen_size * 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
                painter.setPen(pen)
                painter.drawLine(self.last_point, pos)
                self.last_point = pos
                self.update()
            elif self.tool == "shape":
                self.end_point = pos
                self.update()
            elif self.tool == "select" and self.drawing:
                self.selection_rect.setBottomRight(pos)
                self.update()
        elif self.dragging_selection:
            new_top_left = pos - self.selection_offset
            self.selection_rect.moveTo(new_top_left)
            self.update()
        elif self.panning:
            delta = event.position() - self.pan_start_pos
            self.offset += delta
            self.pan_start_pos = event.position()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self.map_to_canvas(event.position())
            if self.drawing:
                if self.tool == "shape" and self.shape:
                    painter = QPainter(self.pixmap)
                    pen = QPen(self.pen_color, self.pen_size)
                    painter.setPen(pen)
                    brush_color = QColor(self.pen_color)
                    brush_color.setAlpha(50)
                    painter.setBrush(brush_color)
                    rect = QRectF(self.start_point, pos)
                    if self.shape == "rectangle":
                        painter.drawRect(rect)
                    elif self.shape == "ellipse":
                        painter.drawEllipse(rect)
                    elif self.shape == "heart":
                        path = self._heart_path(rect)
                        painter.drawPath(path)
                    self.update()
                self.drawing = False
            elif self.dragging_selection:
                self.dragging_selection = False
            elif self.panning:
                self.panning = False

    def _heart_path(self, rect):
        path = QPainterPath()
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        path.moveTo(x + w/2, y + h/5)
        path.cubicTo(x + w/2, y, x, y, x, y + h/3)
        path.cubicTo(x, y + h*2/3, x + w/2, y + h*4/5, x + w/2, y + h)
        path.cubicTo(x + w/2, y + h*4/5, x + w, y + h*2/3, x + w, y + h/3)
        path.cubicTo(x + w, y, x + w/2, y, x + w/2, y + h/5)
        path.closeSubpath()
        return path

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)

        painter.translate(self.offset)
        painter.scale(self.scale_factor, self.scale_factor)

        painter.drawPixmap(0, 0, self.pixmap)

        if self.drawing and self.tool == "shape" and self.shape:
            pen = QPen(self.pen_color, self.pen_size, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            brush_color = QColor(self.pen_color)
            brush_color.setAlpha(50)
            painter.setBrush(brush_color)
            rect = QRectF(self.start_point, self.end_point)
            if self.shape == "rectangle":
                painter.drawRect(rect)
            elif self.shape == "ellipse":
                painter.drawEllipse(rect)
            elif self.shape == "heart":
                path = self._heart_path(rect)
                painter.drawPath(path)

        if self.selection_rect:
            pen = QPen(Qt.GlobalColor.blue, 2, Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self.selection_rect)

    def map_to_canvas(self, pointf):
        return (pointf - self.offset) / self.scale_factor

    def wheelEvent(self, event: QWheelEvent):
        modifiers = event.modifiers()
        delta = event.angleDelta().y()

        if modifiers == Qt.KeyboardModifier.ControlModifier:
            zoom_speed = 0.0015
            old_scale = self.scale_factor
            self.scale_factor += delta * zoom_speed
            self.scale_factor = max(0.1, min(10, self.scale_factor))
            cursor_pos = event.position()
            cursor_pos_before = (cursor_pos - self.offset) / old_scale
            self.offset = cursor_pos - cursor_pos_before * self.scale_factor
            self.update()

        elif modifiers == (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
            pan_speed = 1.0
            self.offset.setX(self.offset.x() + delta * pan_speed)
            self.update()

        elif modifiers == Qt.KeyboardModifier.ShiftModifier:
            pan_speed = 1.0
            self.offset.setY(self.offset.y() + delta * pan_speed)
            self.update()

    def paste_image(self):
        clipboard = QGuiApplication.clipboard()
        mime_data = clipboard.mimeData()
        if mime_data.hasImage():
            img = clipboard.image()
            if not img.isNull():
                painter = QPainter(self.pixmap)
                painter.drawImage(0, 0, img)
                self.update()

    def save_image(self, path=None):
        if not path:
            path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg)")
        if path:
            self.pixmap.save(path)
