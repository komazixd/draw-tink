# components/toolbar.py
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QComboBox, QSlider, QColorDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class ToolBar(QWidget):
    def __init__(self, canvas):
        super().__init__()

        self.canvas = canvas  # link to canvas to send updates

        self.setFixedHeight(50)  # fix toolbar height so it doesn't stretch

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Tool selection
        self.tool_label = QLabel("Tool:")
        self.tool_combo = QComboBox()
        self.tool_combo.addItems(["Pen", "Eraser", "Fill", "Rectangle", "Ellipse"])
        self.tool_combo.currentTextChanged.connect(self.tool_changed)

        # Size slider
        self.size_label = QLabel("Size:")
        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(1, 50)
        self.size_slider.setValue(5)
        self.size_slider.valueChanged.connect(self.size_changed)

        # Opacity slider
        self.opacity_label = QLabel("Opacity:")
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.opacity_changed)

        # Color picker button
        self.color_button = QPushButton("Color")
        self.color_button.clicked.connect(self.pick_color)

        # Add widgets to layout
        layout.addWidget(self.tool_label)
        layout.addWidget(self.tool_combo)

        layout.addWidget(self.size_label)
        layout.addWidget(self.size_slider)

        layout.addWidget(self.opacity_label)
        layout.addWidget(self.opacity_slider)

        layout.addWidget(self.color_button)

        layout.addStretch()

        self.setLayout(layout)

    def tool_changed(self, text):
        self.canvas.set_tool(text)

    def size_changed(self, value):
        self.canvas.set_brush_size(value)

    def opacity_changed(self, value):
        self.canvas.set_opacity(value / 100)

    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.set_brush_color(color)
