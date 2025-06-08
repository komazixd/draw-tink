# components/templatemanager.py
class TemplateManager:
    def __init__(self):
        self.templates = []

    def save_template(self, name, pixmap):
        self.templates.append((name, pixmap.copy()))

    def load_template(self, name):
        for tmpl_name, pix in self.templates:
            if tmpl_name == name:
                return pix.copy()
        return None

    def list_templates(self):
        return [name for name, _ in self.templates]
