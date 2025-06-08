from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QColorDialog, QLabel, QSlider
from PyQt6.QtCore import Qt


class ToolBar(QWidget):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas

        layout = QHBoxLayout()

        # Color Picker
        color_btn = QPushButton("Select Color")
        color_btn.clicked.connect(self.select_color)
        layout.addWidget(color_btn)

        # Undo / Redo
        undo_btn = QPushButton("Undo")
        undo_btn.clicked.connect(self.canvas.undo)
        layout.addWidget(undo_btn)

        redo_btn = QPushButton("Redo")
        redo_btn.clicked.connect(self.canvas.redo)
        layout.addWidget(redo_btn)

        # Pen size slider
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setMinimum(1)
        self.size_slider.setMaximum(50)
        self.size_slider.setValue(self.canvas.pen_size)
        self.size_slider.valueChanged.connect(self.change_pen_size)
        layout.addWidget(QLabel("Pen Size"))
        layout.addWidget(self.size_slider)

        # Tool buttons
        pen_btn = QPushButton("Pen")
        pen_btn.clicked.connect(lambda: self.canvas.set_tool("pen"))
        layout.addWidget(pen_btn)

        eraser_btn = QPushButton("Eraser")
        eraser_btn.clicked.connect(lambda: self.canvas.set_tool("eraser"))
        layout.addWidget(eraser_btn)

        rect_btn = QPushButton("Rectangle")
        rect_btn.clicked.connect(lambda: self.canvas.set_shape("rectangle"))
        layout.addWidget(rect_btn)

        ellipse_btn = QPushButton("Ellipse")
        ellipse_btn.clicked.connect(lambda: self.canvas.set_shape("ellipse"))
        layout.addWidget(ellipse_btn)

        heart_btn = QPushButton("Heart")
        heart_btn.clicked.connect(lambda: self.canvas.set_shape("heart"))
        layout.addWidget(heart_btn)

        pan_btn = QPushButton("Pan")
        pan_btn.clicked.connect(lambda: self.canvas.set_tool("pan"))
        layout.addWidget(pan_btn)

        select_btn = QPushButton("Select")
        select_btn.clicked.connect(lambda: self.canvas.set_tool("select"))
        layout.addWidget(select_btn)

        self.setLayout(layout)

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.set_pen_color(color)

    def change_pen_size(self, value):
        self.canvas.set_pen_size(value)
