from PyQt6.QtWidgets import QApplication
import sys
from dlg.main_window import MainWindow


if __name__ == '__main__':
    app = QApplication([])
    
    window = MainWindow.load_last_session()
    
    if window is None:
        window = MainWindow()
        
    window.show()
    
    sys.exit(app.exec())