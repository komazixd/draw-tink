# main.py
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout
import sys
from components.canvasview import CanvasView
from components.toolbar import ToolBar

class TinkMaker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tink Maker")
        self.setGeometry(100, 100, 1000, 700)

        self.canvas = CanvasView()
        self.toolbar = ToolBar(self.canvas)

        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        container.setLayout(layout)
        self.setCentralWidget(container)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TinkMaker()
    window.show()
    sys.exit(app.exec())
