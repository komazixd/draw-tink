import sys
import os
import urllib.request
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QColorDialog, QFileDialog, QSlider, QListWidget, QListWidgetItem, QGraphicsOpacityEffect,
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QScrollArea, QMenuBar, QMenu
)
from PyQt6.QtGui import (
    QPainter, QPen, QColor, QPixmap, QImage, QWheelEvent, QIcon, QTransform, QAction
)
from PyQt6.QtCore import Qt, QPoint, QSize


APP_VERSION = "1.0"
VERSION_URL = "https://raw.githubusercontent.com/komazixd/draw-tink/main/version.txt"
UPDATE_URL = "https://github.com/komazixd/draw-tink/releases/latest/download/tinkmaker.exe"
MAIN_PY_PATH = "C:/Users/omars/OneDrive/Documents/GitHub/draw-tink/main.py"
MAIN_EXE_PATH = "C:/Users/omars/OneDrive/Documents/GitHub/draw-tink/dist/main.exe"

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(2000, 1600)
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
        self.shape = None
        self.offset = QPoint(0, 0)

    def set_tool(self, tool):
        self.tool = tool

    def set_pen_color(self, color):
        self.pen_color = color

    def set_pen_size(self, size):
        self.pen_size = size

    def set_opacity(self, opacity):
        self.opacity = opacity

    def set_shape(self, shape):
        self.shape = shape

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_point = event.position().toPoint()
            self.undo_stack.append(self.pixmap.copy())
            if self.shape:
                painter = QPainter(self.pixmap)
                pen = QPen(self.pen_color, self.pen_size)
                painter.setPen(pen)
                painter.setOpacity(self.opacity)
                p = self.last_point
                if self.shape == "Heart":
                    painter.drawText(p, "♥")
                self.update()
                self.shape = None
                self.drawing = False

    def mouseMoveEvent(self, event):
        if self.drawing:
            painter = QPainter(self.pixmap)
            pen = QPen(self.pen_color if self.tool != 'eraser' else Qt.GlobalColor.white, self.pen_size)
            painter.setPen(pen)
            painter.setOpacity(self.opacity)
            painter.drawLine(self.last_point, event.position().toPoint())
            self.last_point = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.pixmap)

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

    def paste_image(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Paste Image", "", "Image Files (*.png *.jpg *.bmp)")
        if filename:
            img = QImage(filename)
            painter = QPainter(self.pixmap)
            painter.drawImage(0, 0, img)
            self.update()

class TinkMaker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tink Maker")
        self.canvas = Canvas()
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.init_ui()
        self.check_for_updates()

    def init_ui(self):
        layout = QVBoxLayout()
        tools = QHBoxLayout()

        for name in ["Pen", "Eraser"]:
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, n=name.lower(): self.canvas.set_tool(n))
            tools.addWidget(btn)

        color_btn = QPushButton("Color")
        color_btn.clicked.connect(self.select_color)
        tools.addWidget(color_btn)

        opacity_slider = QSlider(Qt.Orientation.Horizontal)
        opacity_slider.setRange(1, 100)
        opacity_slider.setValue(100)
        opacity_slider.valueChanged.connect(lambda val: self.canvas.set_opacity(val / 100))
        tools.addWidget(QLabel("Opacity"))
        tools.addWidget(opacity_slider)

        size_slider = QSlider(Qt.Orientation.Horizontal)
        size_slider.setRange(1, 50)
        size_slider.setValue(5)
        size_slider.valueChanged.connect(self.canvas.set_pen_size)
        tools.addWidget(QLabel("Size"))
        tools.addWidget(size_slider)

        shape_btn = QPushButton("Heart Shape")
        shape_btn.clicked.connect(lambda: self.canvas.set_shape("Heart"))
        tools.addWidget(shape_btn)

        for name, func in [("Undo", self.canvas.undo), ("Redo", self.canvas.redo)]:
            btn = QPushButton(name)
            btn.clicked.connect(func)
            tools.addWidget(btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.canvas.save_image)
        tools.addWidget(save_btn)

        paste_btn = QPushButton("Paste Image")
        paste_btn.clicked.connect(self.canvas.paste_image)
        tools.addWidget(paste_btn)

        brightness_slider = QSlider(Qt.Orientation.Horizontal)
        brightness_slider.setRange(30, 255)
        brightness_slider.setValue(255)
        brightness_slider.valueChanged.connect(self.set_brightness)
        tools.addWidget(QLabel("Brightness"))
        tools.addWidget(brightness_slider)

        credit = QLabel("Credits: @infiniteinfinite ; dc")
        tools.addWidget(credit)

        container = QWidget()
        layout.addLayout(tools)
        layout.addWidget(self.canvas)
        container.setLayout(layout)
        self.setCentralWidget(container)

    def set_brightness(self, value):
        val = value
        self.setStyleSheet(f"background-color: rgb({val}, {val}, {val}); color: black;")

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.set_pen_color(color)

    def check_for_updates(self):
        try:
            with urllib.request.urlopen(VERSION_URL) as response:
                latest_version = response.read().decode("utf-8").strip()
                if latest_version != APP_VERSION:
                    with open(MAIN_PY_PATH, "r") as src:
                        with open("updated_main.py", "w") as dst:
                            dst.write(src.read())
                    os.system(f'pyinstaller --noconfirm --onefile --windowed --name "main" updated_main.py')
                    os.replace("dist/main.exe", MAIN_EXE_PATH)
        except Exception as e:
            print(f"Update check failed: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TinkMaker()
    window.show()
    sys.exit(app.exec())