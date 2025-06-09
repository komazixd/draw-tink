import sys
import os
import json
import urllib.request
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QColorDialog, QFileDialog, QSlider, QMessageBox,
)
from PyQt6.QtGui import (
    QPainter, QPen, QColor, QMouseEvent, QPixmap, QIcon, QAction
)
from PyQt6.QtCore import Qt, QPoint, QSize, QTimer

GITHUB_VERSION_URL = "https://raw.githubusercontent.com/komazixd/draw-tink/main/version.txt"
GITHUB_EXE_URL = "https://github.com/komazixd/draw-tink/releases/latest/download/drawverse.exe"  # put your actual EXE release URL here

APP_VERSION = "1.0"  # update this version manually when you upload new EXE

SAVE_FOLDER = os.path.expanduser("~/.drawverse/")
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1000, 800)
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(Qt.GlobalColor.white)
        self.pen_color = QColor('black')
        self.pen_size = 5
        self.drawing = False
        self.tool = 'pen'
        self.last_point = QPoint()
        self.undo_stack = []
        self.redo_stack = []

        # ruler support
        self.show_ruler = False
        self.ruler_spacing = 20

    def set_tool(self, tool):
        self.tool = tool

    def set_pen_color(self, color):
        self.pen_color = color

    def set_pen_size(self, size):
        self.pen_size = size

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = True
            self.last_point = event.position().toPoint()
            self.undo_stack.append(self.pixmap.copy())

    def mouseMoveEvent(self, event):
        if self.drawing:
            painter = QPainter(self.pixmap)
            pen = QPen(self.pen_color if self.tool != 'eraser' else Qt.GlobalColor.white, self.pen_size, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(self.last_point, event.position().toPoint())
            self.last_point = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    def paintEvent(self, event):
        canvas_painter = QPainter(self)
        canvas_painter.drawPixmap(self.rect(), self.pixmap)

        if self.show_ruler:
            pen = QPen(QColor(200, 200, 200), 1)
            canvas_painter.setPen(pen)
            # vertical ruler lines
            for x in range(0, self.width(), self.ruler_spacing):
                canvas_painter.drawLine(x, 0, x, 10)
                if x % 100 == 0:
                    canvas_painter.drawText(x + 2, 20, str(x))
            # horizontal ruler lines
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

class DrawingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DrawVerse")
        self.setStyleSheet("""
            QWidget { background-color: #121212; color: #eee; font-family: Arial; }
            QPushButton {
                background-color: #1f1f1f; border-radius: 10px; padding: 7px 15px;
            }
            QPushButton:hover {
                background-color: #333333;
            }
            QLabel {
                padding-left: 5px;
            }
            QSlider::handle:horizontal {
                background: #eee; border-radius: 7px; width: 14px; margin: -5px 0;
            }
        """)
        self.canvas = Canvas()
        self.init_ui()
        self.check_for_updates()

    def init_ui(self):
        main_layout = QVBoxLayout()
        tool_layout = QHBoxLayout()

        # Pen button
        pen_button = QPushButton("Pen")
        pen_button.clicked.connect(lambda: self.canvas.set_tool("pen"))
        tool_layout.addWidget(pen_button)

        # Eraser button
        eraser_button = QPushButton("Eraser")
        eraser_button.clicked.connect(lambda: self.canvas.set_tool("eraser"))
        tool_layout.addWidget(eraser_button)

        # Color picker
        color_button = QPushButton("Color")
        color_button.clicked.connect(self.select_color)
        tool_layout.addWidget(color_button)

        # Pen size slider
        size_slider = QSlider(Qt.Orientation.Horizontal)
        size_slider.setMinimum(1)
        size_slider.setMaximum(50)
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

        # Save/load drawing
        save_button = QPushButton("Save Drawing")
        save_button.clicked.connect(self.save_drawing)
        tool_layout.addWidget(save_button)

        load_button = QPushButton("Load Drawing")
        load_button.clicked.connect(self.load_drawing)
        tool_layout.addWidget(load_button)

        # Ruler toggle
        ruler_button = QPushButton("Toggle Ruler")
        ruler_button.setCheckable(True)
        ruler_button.clicked.connect(self.toggle_ruler)
        tool_layout.addWidget(ruler_button)

        # Check updates button (manual)
        update_button = QPushButton("Check for Updates")
        update_button.clicked.connect(self.check_for_updates)
        tool_layout.addWidget(update_button)

        container = QWidget()
        main_layout.addLayout(tool_layout)
        main_layout.addWidget(self.canvas)
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.set_pen_color(color)

    def save_drawing(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Drawing", SAVE_FOLDER, "PNG Files (*.png);;JPEG Files (*.jpg)")
        if filepath:
            self.canvas.save_image(filepath)
            QMessageBox.information(self, "Saved", f"Drawing saved to {filepath}")

    def load_drawing(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Load Drawing", SAVE_FOLDER, "PNG Files (*.png);;JPEG Files (*.jpg)")
        if filepath:
            self.canvas.load_image(filepath)

    def toggle_ruler(self, checked):
        self.canvas.show_ruler = checked
        self.canvas.update()

    def check_for_updates(self):
        try:
            with urllib.request.urlopen(GITHUB_VERSION_URL) as response:
                latest_version = response.read().decode().strip()
                if latest_version != APP_VERSION:
                    reply = QMessageBox.question(self, "Update Available",
                        f"A new version ({latest_version}) is available. Do you want to download it?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    if reply == QMessageBox.StandardButton.Yes:
                        self.download_update()
                else:
                    QMessageBox.information(self, "Up to Date", "You are using the latest version.")
        except Exception as e:
            print("Update check failed:", e)

    def download_update(self):
        try:
            update_path = os.path.join(SAVE_FOLDER, "drawverse_update.exe")
            urllib.request.urlretrieve(GITHUB_EXE_URL, update_path)
            QMessageBox.information(self, "Downloaded",
                f"Update downloaded to:\n{update_path}\nRun it to update the app.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to download update: {e}")

def main():
    app = QApplication(sys.argv)
    window = DrawingApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
