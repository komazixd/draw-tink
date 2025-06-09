from PyQt6.QtWidgets import (
    QWidget, QPushButton, QLabel, QSlider, QColorDialog,
    QFileDialog, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt

class ToolBar(QWidget):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(5, 5, 5, 5)

        pen_btn = QPushButton("Pen")
        pen_btn.clicked.connect(lambda: self.canvas.set_tool("pen"))
        layout.addWidget(pen_btn)

        eraser_btn = QPushButton("Eraser")
        eraser_btn.clicked.connect(lambda: self.canvas.set_tool("eraser"))
        layout.addWidget(eraser_btn)

        color_btn = QPushButton("Color")
        color_btn.clicked.connect(self.select_color)
        layout.addWidget(color_btn)

        size_label = QLabel("Size")
        layout.addWidget(size_label)

        size_slider = QSlider(Qt.Orientation.Horizontal)
        size_slider.setMinimum(1)
        size_slider.setMaximum(50)
        size_slider.setValue(5)
        size_slider.valueChanged.connect(lambda val: self.canvas.set_pen_size(val))
        layout.addWidget(size_slider)

        undo_btn = QPushButton("Undo")
        undo_btn.clicked.connect(self.canvas.undo)
        layout.addWidget(undo_btn)

        redo_btn = QPushButton("Redo")
        redo_btn.clicked.connect(self.canvas.redo)
        layout.addWidget(redo_btn)

        save_btn = QPushButton("Save Drawing")
        save_btn.clicked.connect(self.save_drawing)
        layout.addWidget(save_btn)

        load_btn = QPushButton("Load Drawing")
        load_btn.clicked.connect(self.load_drawing)
        layout.addWidget(load_btn)

        ruler_btn = QPushButton("Toggle Ruler")
        ruler_btn.setCheckable(True)
        ruler_btn.clicked.connect(self.toggle_ruler)
        layout.addWidget(ruler_btn)

        update_btn = QPushButton("Check for Updates")
        update_btn.clicked.connect(self.canvas.window().check_for_updates)
        layout.addWidget(update_btn)

        self.setLayout(layout)

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.set_pen_color(color)

    def save_drawing(self):
        filepath, _ = QFileDialog.getSaveFileName(self, "Save Drawing", "", "PNG Files (*.png);;JPEG Files (*.jpg)")
        if filepath:
            self.canvas.save_image(filepath)
            QMessageBox.information(self, "Saved", f"Drawing saved to {filepath}")

    def load_drawing(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Load Drawing", "", "PNG Files (*.png);;JPEG Files (*.jpg)")
        if filepath:
            self.canvas.load_image(filepath)

    def toggle_ruler(self, checked):
        self.canvas.show_ruler = checked
        self.canvas.update()
