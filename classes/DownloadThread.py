import os
import json
import sys
import yt_dlp
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, QCheckBox, QFileDialog, QWidget, QMessageBox, QProgressBar
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt


class DownloadThread(QThread):
    progress = pyqtSignal(int)
    error = pyqtSignal(str)
    finished = pyqtSignal(str)

    def __init__(self, url, quality, download_path, ffmpeg_path, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.url = url
        self.quality = quality
        self.download_path = download_path
        self.ffmpeg_path = ffmpeg_path

    def run(self):
        self.downloaded = False
        while not self.downloaded:
            ydl_opts = {
                    'format': f'bestvideo[height<={self.quality}]+bestaudio/best[height<={self.quality}]',
                    'outtmpl': f'{self.download_path}/%(title)s.%(ext)s',
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor'
                    }],
                    'ffmpeg_location': self.ffmpeg_path,
                    'progress_hooks': [self.progress_hook]
            }
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([self.url])
            except AttributeError:
                self.downloaded = True
                break
            except Exception as e:
                print(str(e))
                continue

    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = int(d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100)
            self.progress.emit(percent)
