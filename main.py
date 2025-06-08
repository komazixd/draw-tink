import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QColorDialog
from components.canvasview import CanvasView
from components.template_manager import TemplateManager

class TinkMaker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tink Maker")
        self.canvas = CanvasView()
        self.template_manager = TemplateManager()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        btn_layout = QHBoxLayout()

        color_btn = QPushButton("Select Color")
        color_btn.clicked.connect(self.select_color)
        btn_layout.addWidget(color_btn)

        undo_btn = QPushButton("Undo")
        undo_btn.clicked.connect(self.canvas.undo)
        btn_layout.addWidget(undo_btn)

        redo_btn = QPushButton("Redo")
        redo_btn.clicked.connect(self.canvas.redo)
        btn_layout.addWidget(redo_btn)

        layout.addLayout(btn_layout)
        layout.addWidget(self.canvas)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.set_pen_color(color)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TinkMaker()
    window.show()
    sys.exit(app.exec())
