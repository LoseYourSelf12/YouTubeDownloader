import os
import json
import sys
import yt_dlp
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QCheckBox, QFileDialog, QWidget, QMessageBox, QProgressBar
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt

# Загрузка конфигурации
with open("config.json", 'r') as f:
    config = json.load(f)

try:
    API_KEY = config['API_KEY']
except KeyError:
    print('API KEY not found')
    API_KEY = None

class DownloadThread(QThread):
    progress = pyqtSignal(int)
    error = pyqtSignal(str)
    finished = pyqtSignal(str)

    def __init__(self, url, quality, download_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = url
        self.quality = quality
        self.download_path = download_path
        self.max_retries = 3
        self.retry_count = 0

    def run(self):
        while self.retry_count < self.max_retries:
            ydl_opts = {
                'format': f'bestvideo[height<={self.quality}]+bestaudio/best[height<={self.quality}]',
                'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor'
                }],
                'ffmpeg_location': config["ffmpeg_PATH"],  # specify the location if it's not in PATH
                'progress_hooks': [self.progress_hook]
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            self.finished.emit('Загрузка завершена.')
            break
            

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = int(d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100)
            self.progress.emit(percent)

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
        
        self.delete_button = QPushButton('Удалить все видео', self)
        self.delete_button.clicked.connect(self.delete_videos)
        layout.addWidget(self.delete_button)

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
        
        
        self.download_button.setEnabled(False)
        
        self.current_thread = DownloadThread(url, self.selected_quality, self.download_path)
        self.current_thread.progress.connect(self.update_progress)
        self.current_thread.error.connect(self.handle_error)
        self.current_thread.finished.connect(self.handle_finish)
        self.current_thread.start()
    
    def update_progress(self, percent):
        self.progress_bar.setValue(percent)
    
    def handle_error(self, error_message):
        # reply = QMessageBox.warning(self, 'Ошибка', error_message)
        self.download_video()

    def handle_finish(self, message):
        QMessageBox.information(self, 'Успех', message)
        self.download_button.setEnabled(True)
        self.progress_bar.setValue(100)
    
    def delete_videos(self):
        # Удаление всех скачанных видео
        for file_name in os.listdir(self.download_path):
            file_path = os.path.join(self.download_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
        QMessageBox.information(self, 'Удаление', 'Все видео были удалены.')

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
