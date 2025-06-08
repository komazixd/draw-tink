from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtGui import QPainter, QColor, QPen, QPixmap, QMouseEvent, QWheelEvent, QKeyEvent
from PyQt6.QtCore import Qt, QPoint, QRectF

class CanvasView(QWidget):
    def __init__(self):
        super().__init__()

        # Canvas image where we draw
        self.image = QPixmap(1600, 1200)
        self.image.fill(QColor('white'))

        # Drawing state
        self.drawing = False
        self.last_point = QPoint()

        # Brush settings
        self.brush_color = QColor('black')
        self.brush_size = 5
        self.brush_opacity = 255  # 0-255

        # Zoom & pan
        self.zoom = 1.0
        self.offset = QPoint(0, 0)
        self.panning = False
        self.pan_start = QPoint()

        # Shape tool mode ('brush', 'eraser', 'line', 'rectangle', 'ellipse', 'none')
        self.tool = 'brush'

        # Shape drawing temp vars
        self.shape_start = None
        self.shape_end = None

        # For smooth painting (optional)
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents)

        self.setMinimumSize(800, 600)
        self.setMouseTracking(True)

    def set_brush_color(self, color: QColor):
        self.brush_color = color

    def set_brush_size(self, size: int):
        self.brush_size = max(1, size)

    def set_brush_opacity(self, opacity: int):
        self.brush_opacity = max(0, min(255, opacity))

    def set_tool(self, tool_name: str):
        self.tool = tool_name

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor('white'))

        # Apply zoom and pan transformations
        painter.translate(self.offset)
        painter.scale(self.zoom, self.zoom)

        # Draw the current canvas image
        painter.drawPixmap(0, 0, self.image)

        # If drawing shapes, show preview
        if self.tool in ['line', 'rectangle', 'ellipse'] and self.drawing and self.shape_start and self.shape_end:
            pen = QPen(self.brush_color)
            pen.setWidth(self.brush_size)
            pen.setStyle(Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)

            rect = QRectF(self.shape_start, self.shape_end)
            if self.tool == 'line':
                painter.drawLine(self.shape_start, self.shape_end)
            elif self.tool == 'rectangle':
                painter.drawRect(rect.normalized())
            elif self.tool == 'ellipse':
                painter.drawEllipse(rect.normalized())

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self.transform_pos(event.position().toPoint())
            if self.tool == 'brush' or self.tool == 'eraser':
                self.drawing = True
                self.last_point = pos
                self.draw_point(pos)
            elif self.tool in ['line', 'rectangle', 'ellipse']:
                self.drawing = True
                self.shape_start = pos
                self.shape_end = pos
            elif self.tool == 'pan':
                self.panning = True
                self.pan_start = event.position().toPoint()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = self.transform_pos(event.position().toPoint())
        if self.drawing:
            if self.tool == 'brush':
                self.draw_line(self.last_point, pos)
                self.last_point = pos
            elif self.tool == 'eraser':
                self.erase_line(self.last_point, pos)
                self.last_point = pos
            elif self.tool in ['line', 'rectangle', 'ellipse']:
                self.shape_end = pos
                self.update()
        elif self.panning:
            delta = event.position().toPoint() - self.pan_start
            self.offset += delta
            self.pan_start = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.drawing:
                pos = self.transform_pos(event.position().toPoint())
                if self.tool in ['line', 'rectangle', 'ellipse']:
                    self.shape_end = pos
                    self.draw_shape()
                    self.shape_start = None
                    self.shape_end = None
                self.drawing = False
                self.update()
            if self.panning:
                self.panning = False
                self.setCursor(Qt.CursorShape.ArrowCursor)

    def wheelEvent(self, event: QWheelEvent):
        angle = event.angleDelta().y()
        factor = 1.15 if angle > 0 else 1 / 1.15
        old_zoom = self.zoom
        self.zoom *= factor
        self.zoom = max(0.1, min(self.zoom, 5.0))

        # Adjust offset to zoom towards cursor
        cursor_pos = event.position().toPoint()
        before_scale = (cursor_pos - self.offset) / old_zoom
        after_scale = (cursor_pos - self.offset) / self.zoom
        self.offset += (after_scale - before_scale) * self.zoom

        self.update()

    def transform_pos(self, pos: QPoint) -> QPoint:
        # Convert widget coords to image coords considering zoom and pan
        x = (pos.x() - self.offset.x()) / self.zoom
        y = (pos.y() - self.offset.y()) / self.zoom
        return QPoint(int(x), int(y))

    def draw_point(self, pos: QPoint):
        painter = QPainter(self.image)
        pen = QPen(self.brush_color)
        pen.setWidth(self.brush_size)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

        color = QColor(self.brush_color)
        color.setAlpha(self.brush_opacity)
        pen.setColor(color)

        painter.setPen(pen)
        painter.drawPoint(pos)
        self.update()

    def draw_line(self, start: QPoint, end: QPoint):
        painter = QPainter(self.image)
        pen = QPen(self.brush_color)
        pen.setWidth(self.brush_size)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

        color = QColor(self.brush_color)
        color.setAlpha(self.brush_opacity)
        pen.setColor(color)

        painter.setPen(pen)
        painter.drawLine(start, end)
        self.update()

    def erase_line(self, start: QPoint, end: QPoint):
        painter = QPainter(self.image)
        pen = QPen(QColor('white'))
        pen.setWidth(self.brush_size * 2)  # Eraser bigger than brush
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

        painter.setPen(pen)
        painter.drawLine(start, end)
        self.update()

    def draw_shape(self):
        painter = QPainter(self.image)
        pen = QPen(self.brush_color)
        pen.setWidth(self.brush_size)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        rect = QRectF(self.shape_start, self.shape_end).normalized()
        if self.tool == 'line':
            painter.drawLine(self.shape_start, self.shape_end)
        elif self.tool == 'rectangle':
            painter.drawRect(rect)
        elif self.tool == 'ellipse':
            painter.drawEllipse(rect)

        self.update()
