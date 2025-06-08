# components/shapes.py

from PyQt6.QtGui import QPainter, QPen, QColor, QPainterPath, QPixmap, QImage
from PyQt6.QtCore import QRectF, QPointF

class Shape:
    def __init__(self, start_pos, pen_color=QColor(0,0,0), pen_width=2, opacity=1.0):
        self.start_pos = start_pos
        self.end_pos = start_pos
        self.pen_color = pen_color
        self.pen_width = pen_width
        self.opacity = opacity

    def update_end(self, pos):
        self.end_pos = pos

    def paint(self, painter: QPainter):
        pass

    def contains(self, pos):
        # Basic bounding box hit test
        rect = QRectF(self.start_pos, self.end_pos).normalized()
        return rect.contains(pos)

class RectangleShape(Shape):
    def paint(self, painter: QPainter):
        painter.save()
        pen = QPen(self.pen_color, self.pen_width)
        painter.setPen(pen)
        painter.setOpacity(self.opacity)
        rect = QRectF(self.start_pos, self.end_pos).normalized()
        painter.drawRect(rect)
        painter.restore()

class EllipseShape(Shape):
    def paint(self, painter: QPainter):
        painter.save()
        pen = QPen(self.pen_color, self.pen_width)
        painter.setPen(pen)
        painter.setOpacity(self.opacity)
        rect = QRectF(self.start_pos, self.end_pos).normalized()
        painter.drawEllipse(rect)
        painter.restore()

class HeartShape(Shape):
    def paint(self, painter: QPainter):
        painter.save()
        painter.setOpacity(self.opacity)
        pen = QPen(self.pen_color, self.pen_width)
        painter.setPen(pen)
        rect = QRectF(self.start_pos, self.end_pos).normalized()

        path = QPainterPath()

        w = rect.width()
        h = rect.height()
        x = rect.left()
        y = rect.top()

        path.moveTo(x + w/2, y + h*0.9)
        path.cubicTo(x + w*1.4, y + h*0.35,
                     x + w*0.8, y - h*0.4,
                     x + w/2, y + h*0.25)
        path.cubicTo(x + w*0.2, y - h*0.4,
                     x - w*0.4, y + h*0.35,
                     x + w/2, y + h*0.9)

        painter.drawPath(path)
        painter.restore()

class ImageShape(Shape):
    def __init__(self, image: QImage, pos: QPointF):
        super().__init__(pos)
        self.image = image
        self.pos = pos

    def paint(self, painter: QPainter):
        painter.save()
        painter.setOpacity(1.0)
        painter.drawImage(self.pos, self.image)
        painter.restore()

    def contains(self, pos):
        rect = QRectF(self.pos, self.image.size())
        return rect.contains(pos)
