from ui.ui_main_window import Ui_MainWindow
from PyQt6.QtWidgets import QMainWindow, QFileDialog
import _pickle as pickle
import os
from dlg.error_dialog import ErrorDialog
from PyQt6.QtGui import QIcon
import traceback

class MainWindow(QMainWindow, Ui_MainWindow):
    _appTitle = "PyQtToCpp"
    _appExt = "pyqt-c++"
    _lastSessionPtr = 'last-session.pickle'
    
    def __init__(self, parent=None, pickled=False):
        super().__init__(parent)
        super().__init__()
        self.setupUi(self)
        self._saveFilename = None
        self._saved = False
        self._appEntrypoint = None
        self._runtimeCheckFolder = None
        
        # TODO: figure out how to do this in Resource file in PyQt6 (?)
        self.setWindowIcon(QIcon("img/Python_and_Qt.svg"))
        
        self.setWindowTitle(self._appTitle)
        
        if not pickled:
            self.finish_setup()            
            
    def __setstate__(self, data):
        self.__init__(pickled=True)
        self.set_app_entrypoint(data['app entrypoint'])
        self.set_runtime_check_folder(data['runtime check folder'])
        self.setWindowTitle(self._appTitle)
        self.finish_setup()
        
    def __getstate__(self):
        return {
            'app entrypoint' : self.app_entrypoint(),
            'runtime check folder' : self.runtime_check_folder(),
        }
    
    def set_app_entrypoint(self, entrypoint):
        if self._appEntrypoint != entrypoint:
            self._appEntrypoint = entrypoint
            self.pythonAppEntrypointLine.setText(entrypoint)
            self.app_changes_made()
            
    def app_entrypoint(self):
        return self._appEntrypoint
    
    def set_runtime_check_folder(self, folder):
        if self._runtimeCheckFolder != folder:
            self._runtimeCheckFolder = folder
            self.runtimeTypingFolderLine.setText(folder)
            self.app_changes_made()
            
    def runtime_check_folder(self):
        return self._runtimeCheckFolder
            
    def app_changes_made(self):
        self.setWindowTitle(f'{self._appTitle}*')
            
    def finish_setup(self):
        self.actionSaveProject.triggered.connect(self.save)
        self.actionSave_as.triggered.connect(self.save_as)
        self.pythonAppEntrypointLine.textChanged.connect(self.set_app_entrypoint)
        self.chooseAppEntryButton.clicked.connect(self.display_app_entrypoint_dialog)
        self.chooseRuntimeTypingButton.clicked.connect(self.display_runtime_check_folder_dialog)
        
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
            
        except:
            self.display_error_message(MainWindow, MainWindow.save, None, traceback.format_exc(), parent=self)
            
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
        except:
            self.display_app_entrypoint_dialog(MainWindow, MainWindow.save_as, None, traceback.format_exc(), parent=self)
        
    @staticmethod
    def display_error_message(cls, method, args, traceback, parent=None):
        # TODO: switch to exception-based with function / class name, line number /module
        # as well as traceback info
        if not args:
            args = "()"
            
        msg = f"""ERROR in {cls.__name__}.{method.__name__}{args}:
---
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
            
        except:
            self.display_error_message(MainWindow, MainWindow.display_app_entrypoint_dialog, None, traceback.format_exc(), parent=self)
    
    def display_runtime_check_folder_dialog(self):
        try:
            if self._runtimeCheckFolder is None:
                rt_check_folder_dir = '.'
            else:
                rt_check_folder_dir = os.path.dirname(self._runtimeCheckFolder)
                
            rt_check_folder = QFileDialog.getExistingDirectory(
                parent=self, caption="Choose Runtime Type Check Folder",
                directory=rt_check_folder_dir, options=QFileDialog.Option.ShowDirsOnly)
            
            if os.path.exists(rt_check_folder):
                self.set_runtime_check_folder(rt_check_folder)
            
        except:            
            self.display_error_message(MainWindow, MainWindow.display_runtime_check_folder_dialog, None, traceback.format_exc(), parent=self)
            
    @staticmethod
    def load_last_session():
        try:
            if os.path.exists(MainWindow._lastSessionPtr):
                with open(MainWindow._lastSessionPtr, 'rb') as last_session_ptr:
                    last_project_filename = pickle.load(last_session_ptr)
                    
                with open(last_project_filename, 'rb') as last_project_file:
                    window = pickle.load(last_project_file)
                    window._saveFilename = last_project_filename
                
                return window
            
        except:
            MainWindow.display_error_message(MainWindow, MainWindow.save, None, traceback.format_exc())
            
    def save_last_session(self):
        try:
            if self._saveFilename is not None:
                with open(MainWindow._lastSessionPtr, 'wb') as last_session_ptr:
                    pickle.dump(self._saveFilename, last_session_ptr)
        except:
            MainWindow.display_error_message(MainWindow, MainWindow.save, None, traceback.format_exc())
        