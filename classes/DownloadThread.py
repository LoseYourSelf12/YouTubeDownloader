import os
import yt_dlp

from PyQt6.QtCore import QThread, pyqtSignal


class DownloadThread(QThread):
    progress = pyqtSignal(int)
    current_speed = pyqtSignal(str)
    average_speed = pyqtSignal(float)
    elapsed_time = pyqtSignal(float)
    total_size = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, url, quality, download_path, ffmpeg_path, vid_name, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.url = url
        self.quality = quality
        self.download_path = download_path
        self.ffmpeg_path = ffmpeg_path
        self.vid_name = vid_name

    def run(self):
        self.downloaded = False

        ext = 'mp4'
        counter = 0

        base_name = self.vid_name
        while os.path.exists(f'{self.download_path}/{base_name}.{ext}'):
            base_name = f'{self.vid_name}_{counter}'
            counter += 1
        final_name = base_name

        while not self.downloaded:
            ydl_opts = {
                    'format': f'bestvideo[height<={self.quality}]+bestaudio/best[height<={self.quality}]',
                    'outtmpl': f'{self.download_path}/{final_name}.%(ext)s',
                    'postprocessors': [{
                        'key': 'FFmpegVideoConvertor',
                        'preferedformat': 'mp4'
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
            except yt_dlp.utils.ExtractorError as e:
                self.error.emit(str(e))
                break
            except yt_dlp.utils.DownloadError as e:
                self.error.emit(str(e))
                break
            except Exception as e:
                print(str(e))
                continue

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = int(d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100)
            self.progress.emit(percent)
            self.current_speed.emit(f'{d.get("speed", 0)} bytes/s')
            try:
                self.average_speed.emit(d.get('eta', 0))
            except Exception as e:
                self.average_speed.emit(0.0)
            
            self.elapsed_time.emit(d.get('elapsed', 0))
            self.total_size.emit(d.get('total_bytes', 0))
        if d['status'] == 'finished':
            self.downloaded = True
        if d['status'] == 'error':
            self.error.emit(str(d.get('error')))

