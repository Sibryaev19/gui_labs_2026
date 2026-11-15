from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPlainTextEdit, QDialogButtonBox


class QueryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SQL query")
        self.resize(500, 200)

        layout = QVBoxLayout(self)
        self.edit = QPlainTextEdit()
        self.edit.setPlaceholderText("SELECT ...")
        layout.addWidget(self.edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_query(self):
        return self.edit.toPlainText().strip()
