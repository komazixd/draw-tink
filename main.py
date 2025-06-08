import sys
from PyQt6.QtWidgets import QApplication
from components.mainwindow import TinkMaker

def main():
    app = QApplication(sys.argv)
    window = TinkMaker()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
