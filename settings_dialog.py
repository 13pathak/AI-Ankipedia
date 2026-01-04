from aqt.qt import *
import json

class SettingsDialog(QDialog):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("AI Ankipedia Settings")
        self.resize(500, 400)
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Tab 1: Models
        self.models_tab = QWidget()
        self.setup_models_tab()
        self.tabs.addTab(self.models_tab, "AI Models")

        # Tab 2: Prompts
        self.prompts_tab = QWidget()
        self.setup_prompts_tab()
        self.tabs.addTab(self.prompts_tab, "Prompts")

        # Buttons
        # PyQt6 compatibility: Use StandardButton
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def setup_models_tab(self):
        layout = QVBoxLayout()
        self.models_tab.setLayout(layout)
        
        # Simplified for MVP: Use a simple text area for entering JSON config
        # Ideally this would be a list view with Add/Edit dialogs
        
        lbl = QLabel("Configuration (JSON format for Models):")
        layout.addWidget(lbl)
        
        self.models_editor = QPlainTextEdit()
        self.models_editor.setPlaceholderText('[\n  {"id": "gemini", "name": "Gemini", "endpoint": "...", "apiKey": "..."}\n]')
        layout.addWidget(self.models_editor)

    def setup_prompts_tab(self):
        layout = QVBoxLayout()
        self.prompts_tab.setLayout(layout)
        
        lbl = QLabel("Custom Prompts (JSON):")
        layout.addWidget(lbl)
        
        self.prompts_editor = QPlainTextEdit()
        self.prompts_editor.setPlaceholderText('[\n  {"id": "p1", "name": "Simple", "content": "Explain {word}..."}\n]')
        layout.addWidget(self.prompts_editor)

    def load_config(self):
        models = self.config.get('models', [])
        prompts = self.config.get('prompts', [])
        
        self.models_editor.setPlainText(json.dumps(models, indent=2))
        self.prompts_editor.setPlainText(json.dumps(prompts, indent=2))

    def get_config(self):
        # Parse JSON from editors
        try:
            models = json.loads(self.models_editor.toPlainText())
        except:
            models = self.config.get('models', []) # Fallback
            
        try:
            prompts = json.loads(self.prompts_editor.toPlainText())
        except:
            prompts = self.config.get('prompts', [])

        new_config = self.config.copy()
        new_config['models'] = models
        new_config['prompts'] = prompts
        return new_config
