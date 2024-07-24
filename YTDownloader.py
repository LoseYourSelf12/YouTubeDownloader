import os
import json
import sys
import yt_dlp

from PyQt6.QtWidgets import (QMessageBox, QWidget, QVBoxLayout, 
                             QMainWindow, QCheckBox, QPushButton,
                             QLineEdit, QProgressBar, QFileDialog, 
                             QApplication, QLabel)


from classes.MessageBoxWarning import MessageBoxWarning
from classes.DownloadThread import DownloadThread
from classes.DeleteVideosDialog import DeleteVideosDialog


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

        self.video_info = []

        self.load_saved_videos()
    
    def initUI(self):
        layout = QVBoxLayout()
        
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText('Введите ссылку на видео')
        layout.addWidget(self.url_input)

        self.vid_name = QLineEdit(self)
        self.vid_name.setPlaceholderText('Введите любое название')
        layout.addWidget(self.vid_name)
        
        self.quality_checkboxes = []
        for quality in ['480', '720', '1080']:
            checkbox = QCheckBox(f'{quality}p', self)
            checkbox.clicked.connect(self.on_quality_checkbox_clicked)
            layout.addWidget(checkbox)
            self.quality_checkboxes.append(checkbox)
        
        self.download_path_input = QLabel(self)
        self.download_path_input.setText('Select folder')
        layout.addWidget(self.download_path_input)
        
        select_path_button = QPushButton('Выбрать папку', self)
        select_path_button.clicked.connect(self.select_path)
        layout.addWidget(select_path_button)
        
        self.download_button = QPushButton('Скачать', self)
        self.download_button.clicked.connect(self.download_video)
        layout.addWidget(self.download_button)

        # Кнопка для удаления скачанных видео
        self.delete_videos_button = QPushButton("Удалить скачанные видео", self)
        self.delete_videos_button.clicked.connect(self.delete_videos)
        layout.addWidget(self.delete_videos_button)
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.warning_lable = QLabel(self)
        self.warning_lable.setText('Errors not occurred')
        layout.addWidget(self.warning_lable)


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
        self.warning_lable.setText(str(error_message))

    def delete_videos(self):
        dialog = DeleteVideosDialog(self.video_info)
        if dialog.exec():
            self.video_info = dialog.get_updated_video_info()
            self.save_video_info()

    def save_video_info(self):
        with open("saves.json", "w") as f:
            json.dump(self.video_info, f, indent=4, ensure_ascii=False)

    def load_saved_videos(self):
        if os.path.exists("saves.json"):
            with open("saves.json", "r") as f:
                self.video_info = json.load(f)

    def download_video(self):
        url = self.url_input.text().strip()
        vid_name = self.vid_name.text().replace(' ', '_')
        if not url:
            QMessageBox.warning(self, 'Ошибка', 'Введите URL видео.')
            return
        
        if not vid_name:
            QMessageBox.warning(self, 'Ошибка', 'Введите название видео.')
            return
        
        if not self.selected_quality:
            QMessageBox.warning(self, 'Ошибка', 'Выберите качество видео.')
            return
        
        if not self.download_path:
            QMessageBox.warning(self, 'Ошибка', 'Выберите папку для скачивания.')
            return
        
        self.current_thread = DownloadThread(url, self.selected_quality, self.download_path, FFMPEG_PATH, vid_name)

        # yt = yt_dlp.YoutubeDL().extract_info(url, download=False)
        video_info = {
                "title": vid_name,
                "path": os.path.join(self.download_path, f"{vid_name}.mp4")
            }
        

        self.current_thread.progress.connect(self.update_progress)
        self.current_thread.error.connect(self.handle_error)
        self.current_thread.start()
        self.video_info.append(video_info)
        self.save_video_info()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()