import os
import json
import sys
import yt_dlp
from PyQt6.QtWidgets import (
    QScrollArea, QDialog, QVBoxLayout, QPushButton, QCheckBox, QWidget
)



class DeleteVideosDialog(QDialog):
    def __init__(self, video_info):
        super().__init__()
        self.setWindowTitle("Удалить скачанные видео")
        self.setGeometry(200, 200, 400, 300)
        self.video_info = video_info

        layout = QVBoxLayout()

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)

        self.checkboxes = []
        for video in self.video_info:
            checkbox = QCheckBox(video["title"], self.scroll_content)
            self.scroll_layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)

        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

        self.delete_button = QPushButton("Удалить выбранные", self)
        self.delete_button.clicked.connect(self.delete_selected_videos)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

    def delete_selected_videos(self):
        updated_video_info = []
        for i, checkbox in enumerate(self.checkboxes):
            if not checkbox.isChecked():
                updated_video_info.append(self.video_info[i])
            else:
                try:
                    os.remove(f"{self.video_info[i]["path"]}")
                except FileNotFoundError:
                    pass

        self.video_info = updated_video_info
        self.accept()

    def get_updated_video_info(self):
        return self.video_info