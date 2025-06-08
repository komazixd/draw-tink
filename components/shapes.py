from PyQt6.QtGui import QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import QRect, QPoint

class Shape:
    def __init__(self, x, y, width, height, stroke_color=QColor('black'), fill_color=QColor('transparent')):
        self.rect = QRect(x, y, width, height)
        self.stroke_color = stroke_color
        self.fill_color = fill_color
        self.selected = False

    def draw(self, painter: QPainter):
        raise NotImplementedError

    def contains(self, point: QPoint):
        return self.rect.contains(point)

    def move(self, dx, dy):
        self.rect.translate(dx, dy)

    def resize(self, new_width, new_height):
        self.rect.setWidth(new_width)
        self.rect.setHeight(new_height)

class RectangleShape(Shape):
    def draw(self, painter: QPainter):
        pen = QPen(self.stroke_color, 2)
        brush = QBrush(self.fill_color)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawRect(self.rect)
        if self.selected:
            # draw selection highlight (dashed rectangle)
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(QBrush(Qt.GlobalColor.transparent))
            painter.drawRect(self.rect)

class EllipseShape(Shape):
    def draw(self, painter: QPainter):
        pen = QPen(self.stroke_color, 2)
        brush = QBrush(self.fill_color)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawEllipse(self.rect)
        if self.selected:
            pen.setStyle(Qt.PenStyle.DashLine)
            painter.setPen(pen)
            painter.setBrush(QBrush(Qt.GlobalColor.transparent))
            painter.drawEllipse(self.rect)

# You can add more shapes like HeartShape similarly
