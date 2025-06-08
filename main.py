
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QColorDialog, QFileDialog, QSlider, QComboBox,
    QInputDialog, QListWidget, QListWidgetItem, QGraphicsOpacityEffect
)
from PyQt6.QtGui import (
    QPainter, QPen, QColor, QMouseEvent, QPixmap, QIcon, QImage
)
from PyQt6.QtCore import Qt, QPoint, QSize

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1000, 800)
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(Qt.GlobalColor.white)
        self.pen_color = QColor('black')
        self.pen_size = 5
        self.opacity = 1.0
        self.drawing = False
        self.tool = 'pen'
        self.last_point = QPoint()
        self.undo_stack = []
        self.redo_stack = []

    def set_tool(self, tool):
        self.tool = tool

    def set_pen_color(self, color):
        self.pen_color = color

    def set_pen_size(self, size):
        self.pen_size = size

    def set_opacity(self, opacity):
        self.opacity = opacity

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_point = event.position().toPoint()
            self.undo_stack.append(self.pixmap.copy())

    def mouseMoveEvent(self, event):
        if self.drawing:
            painter = QPainter(self.pixmap)
            pen = QPen(self.pen_color if self.tool != 'eraser' else Qt.GlobalColor.white, self.pen_size)
            painter.setPen(pen)
            if self.tool == 'highlighter':
                effect = QGraphicsOpacityEffect()
                effect.setOpacity(self.opacity)
                painter.setOpacity(self.opacity)
            painter.drawLine(self.last_point, event.position().toPoint())
            self.last_point = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    def paintEvent(self, event):
        canvas_painter = QPainter(self)
        canvas_painter.drawPixmap(self.rect(), self.pixmap)

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

    def save_image(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg)")
        if filename:
            self.pixmap.save(filename)

class DrawingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DrawVerse")
        self.setStyleSheet("background-color: #000; color: #fff;")
        self.canvas = Canvas()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        tool_layout = QHBoxLayout()

        # Pen button
        pen_button = QPushButton("Pen")
        pen_button.clicked.connect(lambda: self.canvas.set_tool("pen"))
        tool_layout.addWidget(pen_button)

        # Highlighter button
        highlighter_button = QPushButton("Highlighter")
        highlighter_button.clicked.connect(lambda: self.canvas.set_tool("highlighter"))
        tool_layout.addWidget(highlighter_button)

        # Eraser button
        eraser_button = QPushButton("Eraser")
        eraser_button.clicked.connect(lambda: self.canvas.set_tool("eraser"))
        tool_layout.addWidget(eraser_button)

        # Color picker
        color_button = QPushButton("Color")
        color_button.clicked.connect(self.select_color)
        tool_layout.addWidget(color_button)

        # Opacity
        opacity_slider = QSlider(Qt.Orientation.Horizontal)
        opacity_slider.setMinimum(1)
        opacity_slider.setMaximum(100)
        opacity_slider.setValue(100)
        opacity_slider.valueChanged.connect(lambda val: self.canvas.set_opacity(val / 100))
        tool_layout.addWidget(QLabel("Opacity"))
        tool_layout.addWidget(opacity_slider)

        # Pen size
        size_slider = QSlider(Qt.Orientation.Horizontal)
        size_slider.setMinimum(1)
        size_slider.setMaximum(100)
        size_slider.setValue(5)
        size_slider.valueChanged.connect(lambda val: self.canvas.set_pen_size(val))
        tool_layout.addWidget(QLabel("Size"))
        tool_layout.addWidget(size_slider)

        # Undo/Redo
        undo_button = QPushButton("Undo")
        undo_button.clicked.connect(self.canvas.undo)
        tool_layout.addWidget(undo_button)

        redo_button = QPushButton("Redo")
        redo_button.clicked.connect(self.canvas.redo)
        tool_layout.addWidget(redo_button)

        # Save
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.canvas.save_image)
        tool_layout.addWidget(save_button)

        container = QWidget()
        main_layout.addLayout(tool_layout)
        main_layout.addWidget(self.canvas)
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.set_pen_color(color)

def main():
    app = QApplication(sys.argv)
    window = DrawingApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
