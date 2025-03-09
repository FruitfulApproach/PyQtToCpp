from ui.ui_error_dialog import Ui_ErrorDialog
from PyQt6.QtWidgets import QDialog
from PyQt6.QtGui import QDesktopServices, QGuiApplication
from PyQt6.QtCore import QUrl

class ErrorDialog(QDialog, Ui_ErrorDialog):
    _githubIssuesForumUrl =  'https://github.com/FruitfulApproach/PyQtToCpp/issues'
    
    def __init__(self, parent=None):
        super().__init__(parent)
        super().__init__()
        self.setupUi(self)
        self.gitHubButton.clicked.connect(self.goto_github_issues_forum)
        self.copyButton.clicked.connect(self.copy_error_text_to_clipboard)
    
    def goto_github_issues_forum(self):
        # TODO
        QDesktopServices.openUrl(QUrl(self._githubIssuesForumUrl))
        
    def copy_error_text_to_clipboard(self):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.errorMessageText.toPlainText())
        self.copyButton.setText(self.copyButton.text() + " ✅")