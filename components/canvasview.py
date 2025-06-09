# components/canvasview.py

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QPixmap, QMouseEvent
from PyQt6.QtCore import Qt, QPoint

class CanvasView(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1000, 800)
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(Qt.GlobalColor.white)

        self.pen_color = QColor('black')
        self.pen_size = 5
        self.tool = 'pen'
        self.drawing = False
        self.last_point = QPoint()
        self.undo_stack = []
        self.redo_stack = []

        self.show_ruler = False
        self.ruler_spacing = 20

    def set_tool(self, tool):
        self.tool = tool

    def set_pen_color(self, color):
        self.pen_color = color

    def set_pen_size(self, size):
        self.pen_size = size

    def toggle_ruler(self, state):
        self.show_ruler = state
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_point = event.position().toPoint()
            self.undo_stack.append(self.pixmap.copy())

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.drawing:
            painter = QPainter(self.pixmap)
            pen = QPen(self.pen_color if self.tool != 'eraser' else Qt.GlobalColor.white,
                       self.pen_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(self.last_point, event.position().toPoint())
            self.last_point = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    def paintEvent(self, event):
        canvas_painter = QPainter(self)
        canvas_painter.drawPixmap(self.rect(), self.pixmap)

        if self.show_ruler:
            pen = QPen(QColor(200, 200, 200), 1)
            canvas_painter.setPen(pen)
            for x in range(0, self.width(), self.ruler_spacing):
                canvas_painter.drawLine(x, 0, x, 10)
                if x % 100 == 0:
                    canvas_painter.drawText(x + 2, 20, str(x))
            for y in range(0, self.height(), self.ruler_spacing):
                canvas_painter.drawLine(0, y, 10, y)
                if y % 100 == 0:
                    canvas_painter.drawText(12, y + 10, str(y))

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

    def save_image(self, filepath):
        self.pixmap.save(filepath)

    def load_image(self, filepath):
        loaded = QPixmap(filepath)
        if not loaded.isNull():
            self.pixmap = loaded.scaled(self.size())
            self.update()
