from ui.ui_main_window import Ui_MainWindow
from PyQt6.QtWidgets import QMainWindow, QFileDialog
import _pickle as pickle
import os
from dlg.error_dialog import ErrorDialog
import sys
import traceback

class MainWindow(QMainWindow, Ui_MainWindow):
    _appTitle = "PyQtToCpp"
    _appExt = "py-to-c++"
    _lastSessionPtr = 'last-session.pickle'
    
    def __init__(self, parent=None, pickled=False):
        super().__init__(parent)
        super().__init__()
        self.setupUi(self)
        self._saveFilename = None
        self._saved = False
        self._appEntrypoint = None
        #self._
        
        self.setWindowTitle(self._appTitle)
        
        if not pickled:
            self.finish_setup()            
            
    def __setstate__(self, data):
        self.__init__(pickled=True)
        self.set_app_entrypoint(data['app entrypoint'])
        self.finish_setup()
        
    def __getstate__(self):
        return {
            'app entrypoint' : self.app_entrypoint(),
        }
    
    def set_app_entrypoint(self, entrypoint):
        if self._appEntrypoint != entrypoint:
            self._appEntrypoint = entrypoint
            self.pythonAppEntrypointLine.setText(entrypoint)
            self.app_changes_made()
            
    def app_entrypoint(self):
        return self._appEntrypoint
            
    def app_changes_made(self):
        self.setWindowTitle(f'{self._appTitle}*')
            
    def finish_setup(self):
        self.actionSaveProject.triggered.connect(self.save)
        self.actionSave_as.triggered.connect(self.save_as)
        self.pythonAppEntrypointLine.textChanged.connect(self.set_app_entrypoint)
        self.chooseAppEntryButton.clicked.connect(self.display_app_entrypoint_dialog)
        
    def app_entrypoint_changed(self, entrypoint):
        if entrypoint != self._appEntrypoint:
            self._appEntrypoint = entrypoint
            self.app_changes_made()
        
    def closeEvent(self, event):
        self.save()
        self.save_last_session()
        super().closeEvent(event)
        
    def save(self):
        if self._saveFilename is None:
            self.save_as()
        
        try:            
            with open(self._saveFilename, 'wb') as save_file:
                pickle.dump(self, save_file)
            self._saved = True
            
            self.setWindowTitle(self._appTitle)
            
        except Exception as e:
            self.display_error_message(str(e))
            
    def save_as(self):
        try:           
            if self._saveFilename is None:
                save_dir = "."
            else:
                save_dir = os.path.dirname(self._saveFilename)
        
            self._saveFilename, _ = QFileDialog.getSaveFileName(
                parent=self, caption="Save Project As",
                directory=save_dir,
                filter=f"{self._appTitle} (*.{self._appExt});; All files (*.*)")
            
            self.save()
        except Exception as e:
            self.display_app_entrypoint_dialog(str(e))
        
    @staticmethod
    def display_error_message(cls, method, traceback, parent, *args):
        # TODO: switch to exception-based with function / class name, line number /module
        # as well as traceback info
        msg = f"""ERROR in {cls.__name__}.{method.__name__}{args}:
-------------------------------------
{traceback}
        """
        
        error_dialog = ErrorDialog(parent)
        error_dialog.errorMessageText.setPlainText(msg)
        error_dialog.exec()
        
    def display_app_entrypoint_dialog(self):
        try:                
            if self._appEntrypoint is None:
                entrypoint_dir = '.'
            else:
                entrypoint_dir = os.path.dirname(self._appEntrypoint)
                
            app_entrypoint, _ = QFileDialog.getOpenFileName(
                parent=self, caption='Choose App Entrypoint (the "main.py")',
                directory=entrypoint_dir, filter="Python files (*.py);; All files (*.*)",
                initialFilter="Python files (*.py)")
            
            if os.path.exists(app_entrypoint):
                self.set_app_entrypoint(app_entrypoint)                                
            
        except Exception as e:
            self.display_error_message(str(e))
            
    @staticmethod
    def load_last_session():
        try:
            if os.path.exists(MainWindow._lastSessionPtr):
                with open(MainWindow._lastSessionPtr, 'rb') as last_session_ptr:
                    last_project_file = pickle.load(last_session_ptr)
                    
                with open(last_project_file, 'rb') as last_project_file:
                    window = pickle.load(last_project_file)
                
                return window
            
        except Exception as e:
            MainWindow.display_error_message(MainWindow, MainWindow.save, traceback.format_exc(), None)
            
    def save_last_session(self):
        try:
            if self._saveFilename is not None:
                with open(MainWindow._lastSessionPtr, 'wb') as last_session_ptr:
                    pickle.dump(last_session_ptr, self._saveFilename)
        except Exception as e:
            MainWindow.display_error_message(MainWindow, MainWindow.save, traceback.format_exc())
        