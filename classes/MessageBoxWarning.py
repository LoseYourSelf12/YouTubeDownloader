import sys

from PyQt6.QtWidgets import QMainWindow, QMessageBox, QApplication

class MainWindow(QMainWindow):
    def __init__(self, warning_type):
        super().__init__()

        self.setWindowTitle('Warning')

        if warning_type == 'API_KEY':
            QMessageBox.warning(self, 'Warning', 'API key not found!\nRun Setup.exe!')
        elif warning_type == 'PATH':
            QMessageBox.warning(self, 'Warning', 'PATH not found!\nRun Setup.exe')
        elif warning_type == 'FILE':
            QMessageBox.warning(self, 'Warning', 'config.json not found!\nRun Setup.exe')

            
def MessageBoxWarning(warning_type):
    app = QApplication(sys.argv)
    window = MainWindow(warning_type)

    sys.exit()