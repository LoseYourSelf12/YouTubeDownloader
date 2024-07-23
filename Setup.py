import os
import json
import sys
import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox

CONFIG_FILE = "config.json"
ARCHIVE_FILE = "ffmpeg-2024-07-22-git-172da370e7-essentials_build.7z"
SEVEN_ZIP_PATH = "C:\\Program Files\\7-Zip\\7z.exe"  # Замените на путь к вашему 7z.exe

class ConfigWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("YouTube API Key")
        self.setGeometry(100, 100, 300, 100)

        layout = QVBoxLayout()

        self.key_input = QLineEdit(self)
        self.key_input.setPlaceholderText("Введите ключ API YouTube")
        layout.addWidget(self.key_input)

        save_button = QPushButton("Сохранить", self)
        save_button.clicked.connect(self.save_config)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_config(self):
        api_key = self.key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "Ошибка", "Ключ API не может быть пустым.")
            return

        config = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)

        if 'ffmpeg_PATH' not in config:
            QMessageBox.warning(self, "Ошибка", "Путь к ffmpeg не найден в конфигурации.")
            return

        config['API_KEY'] = api_key

        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)

        QMessageBox.information(self, "Успех", "Конфигурация сохранена.")
        self.close()

def extract_ffmpeg(archive_path, extract_path):
    try:
        command = [SEVEN_ZIP_PATH, 'x', archive_path, f'-o{extract_path}', '-y']
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Ошибка при распаковке архива: {result.stderr}")
            sys.exit(1)

        print(f"Файлы успешно распакованы в {extract_path}.")
    except Exception as e:
        print(f"Ошибка при распаковке архива: {str(e)}")
        sys.exit(1)

def main():
    # Проверка и создание директории для ffmpeg
    extract_dir = os.path.join(os.getcwd())
    if not os.path.exists(extract_dir):
        os.makedirs(extract_dir)

    if not os.path.exists(os.path.join(extract_dir, 'bin')):
        print("Распаковываю ffmpeg...")
        extract_ffmpeg(ARCHIVE_FILE, extract_dir)

        # Запись пути к bin в конфигурационный файл
        config = {"ffmpeg_PATH": os.path.join(extract_dir, 'ffmpeg-2024-07-22-git-172da370e7-essentials_build\\bin')}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    else:
        print("Папка bin уже существует. Пропускаем распаковку.")

    app = QApplication(sys.argv)
    ex = ConfigWindow()
    ex.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
