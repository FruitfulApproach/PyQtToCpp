from PyQt6.QtCore import QThread
from rtti import Rtti
import ast
import os
import shutil

class RttiRunner(QThread):
    def __init__(self, app_entry_filename: str, transformer: ast.NodeTransformer, parent=None):
        super().__init__(parent)
        self._xformer = transformer
        self._appEntryFile = app_entry_filename
        
    def run(self):
        app_entry_filename = self.entry_point_filename()        
        xformer = self.transformer(app_entry_filename)
        
        with open(app_entry_filename, 'rt') as app_entry_source:
            ast_tree = ast.parse(app_entry_source)
            xformer.visit(ast_tree)
        
        exec_file = xformer.output_app_entry_filename()
        exec_dir = os.path.dirname(exec_file)
        exec_file = os.path.basename(exec_file)
        os.chdir(exec_dir)
        os.system(f'python {exec_file}')                
        
    def entry_point_filename(self):
        return self._appEntryFile
        
    def transformer(self):
        return self._xformer