class InstructionManager:
    def __init__(self, templates):
        self.templates = templates
    
    def get_instruction(self, class_name, text):
        template = self.templates.get(
            class_name,
            self.templates["default"]
        )
        return template.format(text)
    
    def add_template(self, class_name, template):
        self.templates[class_name] = template