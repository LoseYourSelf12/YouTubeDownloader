import os
import json
import sys
import yt_dlp

from PyQt6.QtWidgets import (QMessageBox, QWidget, QVBoxLayout, 
                             QMainWindow, QCheckBox, QPushButton,
                             QLineEdit, QProgressBar, QFileDialog, 
                             QApplication)


from classes.MessageBoxWarning import MessageBoxWarning
from classes.DownloadThread import DownloadThread


# Load configuration
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    MessageBoxWarning('FILE')

try:
    API_KEY = config['API_KEY']
except KeyError:
    MessageBoxWarning('API_KEY')

try:
    FFMPEG_PATH = config['ffmpeg_PATH']
except KeyError:
    MessageBoxWarning('PATH')


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('YouTube Downloader')
        self.setGeometry(100, 100, 600, 400)
        
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText('Введите ссылку на видео')
        layout.addWidget(self.url_input)
        
        self.quality_checkboxes = []
        for quality in ['480', '720', '1080']:
            checkbox = QCheckBox(f'{quality}p', self)
            checkbox.clicked.connect(self.on_quality_checkbox_clicked)
            layout.addWidget(checkbox)
            self.quality_checkboxes.append(checkbox)
        
        self.download_path_input = QLineEdit(self)
        self.download_path_input.setPlaceholderText('Выберите путь для скачивания')
        layout.addWidget(self.download_path_input)
        
        select_path_button = QPushButton('Выбрать папку', self)
        select_path_button.clicked.connect(self.select_path)
        layout.addWidget(select_path_button)
        
        self.download_button = QPushButton('Скачать', self)
        self.download_button.clicked.connect(self.download_video)
        layout.addWidget(self.download_button)
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # self.delete_button = QPushButton('Удалить все видео', self)
        # self.delete_button.clicked.connect(self.delete_videos)
        # layout.addWidget(self.delete_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        self.selected_quality = None
        self.download_path = ''
        self.current_thread = None


    def on_quality_checkbox_clicked(self):
        sender = self.sender()
        for checkbox in self.quality_checkboxes:
            if checkbox != sender:
                checkbox.setChecked(False)
        self.selected_quality = sender.text().replace('p', '')
    
    def select_path(self):
        path = QFileDialog.getExistingDirectory(self, 'Выберите папку для скачивания')
        if path:
            self.download_path = path
            self.download_path_input.setText(path)

    def update_progress(self, percent):
        self.progress_bar.setValue(percent)

    def handle_error(self, error_message):
        try:
            self.download_video()
        except AttributeError:
            QMessageBox.warning(self, 'Done', 'Vide download!')
        except Exception:
            self.download_video()
        # reply = QMessageBox.warning(self, 'Ошибка', error_message)
    
    # def handle_finish(self, message):
    #     QMessageBox.information(self, 'Downloaded', message)
    #     self.download_button.setEnabled(True)
    #     self.progress_bar.setValue(0)
        

    def download_video(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, 'Ошибка', 'Введите URL видео.')
            return
        
        if not self.selected_quality:
            QMessageBox.warning(self, 'Ошибка', 'Выберите качество видео.')
            return
        
        if not self.download_path:
            QMessageBox.warning(self, 'Ошибка', 'Выберите папку для скачивания.')
            return
        
        # self.download_button.setEnabled(False)
        
        self.current_thread = DownloadThread(url, self.selected_quality, self.download_path, FFMPEG_PATH)
        self.current_thread.progress.connect(self.update_progress)
        self.current_thread.error.connect(self.handle_error)
        # self.current_thread.finished.connect(self.handle_finish)
        self.current_thread.start()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()