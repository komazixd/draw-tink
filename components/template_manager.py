from PyQt6.QtWidgets import QWidget, QListWidget, QVBoxLayout, QPushButton, QMessageBox

class TemplateManager(QWidget):
    def __init__(self):
        super().__init__()
        self.templates = {
            "Simple Square": self.template_square,
            "Simple Circle": self.template_circle
        }
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.list_widget = QListWidget()
        for name in self.templates.keys():
            self.list_widget.addItem(name)
        layout.addWidget(self.list_widget)

        load_btn = QPushButton("Load Template")
        load_btn.clicked.connect(self.load_template)
        layout.addWidget(load_btn)

        self.setLayout(layout)

    def load_template(self):
        selected = self.list_widget.currentItem()
        if not selected:
            QMessageBox.warning(self, "No selection", "Please select a template to load.")
            return
        template_name = selected.text()
        func = self.templates.get(template_name)
        if func:
            func()
        else:
            QMessageBox.warning(self, "Error", "Template not found.")

    def template_square(self):
        # placeholder for loading a square template - you expand this!
        print("Load square template")

    def template_circle(self):
        # placeholder for loading a circle template - you expand this!
        print("Load circle template")
