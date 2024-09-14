import sys
import os
import glob
import random
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QFileDialog, QLabel, QCheckBox, QSpinBox, QMessageBox, QSplitter)
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PIL import Image
from io import BytesIO

class ImagePlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.image_paths = []
        self.current_image_index = 0
        self.is_randomized_images = False
        self.slideshow_active = False
        self.slideshow_interval = 5000
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_slideshow)

        self.init_ui()

    def init_ui(self):
        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignCenter)

        self.prevButton = QPushButton("<< Previous")
        self.prevButton.clicked.connect(self.show_previous_image)

        self.nextButton = QPushButton("Next >>")
        self.nextButton.clicked.connect(self.show_next_image)

        self.randomize_checkbox = QCheckBox("Randomize Images")
        self.randomize_checkbox.stateChanged.connect(self.toggle_randomize_images)

        self.slideshow_button = QPushButton("Start Slideshow")
        self.slideshow_button.clicked.connect(self.toggle_slideshow)

        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1000, 10000)  # Interval range from 1s to 10s
        self.interval_spinbox.setValue(5000)  # Default to 5 seconds
        self.interval_spinbox.setSuffix(" ms")
        self.interval_spinbox.valueChanged.connect(self.update_interval)

        self.directoryButton = QPushButton("Select Directory")
        self.directoryButton.clicked.connect(self.select_directory)

        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.prevButton)
        controlLayout.addWidget(self.nextButton)
        controlLayout.addWidget(self.randomize_checkbox)
        controlLayout.addWidget(self.slideshow_button)
        controlLayout.addWidget(self.interval_spinbox)
        controlLayout.addWidget(self.directoryButton)

        layout = QVBoxLayout()
        layout.addWidget(self.imageLabel)
        layout.addLayout(controlLayout)

        self.setLayout(layout)

    def show_image(self, path):
        try:
            image = Image.open(path)
            q_image = self.pillow_to_qimage(image)
            pixmap = QPixmap.fromImage(q_image)
            self.imageLabel.setPixmap(pixmap.scaled(self.imageLabel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load image: {str(e)}")

    def pillow_to_qimage(self, pil_image):
        with BytesIO() as buffer:
            pil_image.save(buffer, format='PNG')
            q_image = QImage.fromData(buffer.getvalue())
        return q_image

    def show_previous_image(self):
        if self.image_paths:
            self.current_image_index = (self.current_image_index - 1) % len(self.image_paths)
            self.show_image(self.image_paths[self.current_image_index])

    def show_next_image(self):
        if self.image_paths:
            self.current_image_index = (self.current_image_index + 1) % len(self.image_paths)
            self.show_image(self.image_paths[self.current_image_index])

    def toggle_randomize_images(self, state):
        self.is_randomized_images = (state == Qt.Checked)
        if self.is_randomized_images:
            random.shuffle(self.image_paths)
            self.current_image_index = 0
            self.show_image(self.image_paths[self.current_image_index])

    def toggle_slideshow(self):
        if self.slideshow_active:
            self.slideshow_active = False
            self.slideshow_button.setText("Start Slideshow")
            self.timer.stop()
        else:
            self.slideshow_active = True
            self.slideshow_button.setText("Stop Slideshow")
            self.update_interval()
            self.timer.start()

    def update_interval(self):
        self.slideshow_interval = self.interval_spinbox.value()
        if self.slideshow_active:
            self.timer.setInterval(self.slideshow_interval)

    def update_slideshow(self):
        self.show_next_image()

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            image_extensions = ["*.jpg", "*.jpeg", "*.png"]
            self.image_paths = []
            for ext in image_extensions:
                self.image_paths.extend(glob.glob(os.path.join(directory, ext)))
            if self.image_paths:
                self.current_image_index = 0
                self.show_image(self.image_paths[self.current_image_index])
            else:
                QMessageBox.information(self, "No Images", "No images found in the selected directory.")

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.video_paths = []
        self.current_video_index = 0
        self.is_randomized_videos = False
        self.video_slideshow_active = False
        self.video_slideshow_interval = 5000
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self.update_video_slideshow)

        self.init_ui()

    def init_ui(self):
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()

        self.playButton = QPushButton()
        self.playButton.setIcon(QIcon.fromTheme("media-playback-start"))
        self.playButton.clicked.connect(self.play_pause)

        self.prevButton = QPushButton("<< Previous")
        self.prevButton.clicked.connect(self.play_previous_video)

        self.nextButton = QPushButton("Next >>")
        self.nextButton.clicked.connect(self.play_next_video)

        self.randomize_videos_checkbox = QCheckBox("Randomize Videos")
        self.randomize_videos_checkbox.stateChanged.connect(self.toggle_randomize_videos)

        self.slideshow_video_button = QPushButton("Start Slideshow")
        self.slideshow_video_button.clicked.connect(self.toggle_video_slideshow)

        self.interval_video_spinbox = QSpinBox()
        self.interval_video_spinbox.setRange(1000, 10000)  # Interval range from 1s to 10s
        self.interval_video_spinbox.setValue(5000)  # Default to 5 seconds
        self.interval_video_spinbox.setSuffix(" ms")
        self.interval_video_spinbox.valueChanged.connect(self.update_video_interval)

        self.directoryButton = QPushButton("Select Directory")
        self.directoryButton.clicked.connect(self.select_directory)

        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.prevButton)
        controlLayout.addWidget(self.nextButton)
        controlLayout.addWidget(self.randomize_videos_checkbox)
        controlLayout.addWidget(self.slideshow_video_button)
        controlLayout.addWidget(self.interval_video_spinbox)
        controlLayout.addWidget(self.directoryButton)

        layout = QVBoxLayout()
        layout.addWidget(self.videoWidget)
        layout.addLayout(controlLayout)

        self.setLayout(layout)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.handle_state_change)
        self.mediaPlayer.error.connect(self.handle_error)

        self.video_timer.setInterval(self.video_slideshow_interval)

    def load_video(self, index):
        if self.video_paths:
            try:
                video_path = self.video_paths[index]
                self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
                self.play_pause()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load video: {str(e)}")

    def play_pause(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
            self.playButton.setIcon(QIcon.fromTheme("media-playback-start"))
        else:
            self.mediaPlayer.play()
            self.playButton.setIcon(QIcon.fromTheme("media-playback-pause"))

    def play_previous_video(self):
        if self.video_paths:
            self.current_video_index = (self.current_video_index - 1) % len(self.video_paths)
            self.load_video(self.current_video_index)

    def play_next_video(self):
        if self.video_paths:
            if self.is_randomized_videos:
                self.current_video_index = random.randint(0, len(self.video_paths) - 1)
            else:
                self.current_video_index = (self.current_video_index + 1) % len(self.video_paths)
            self.load_video(self.current_video_index)

    def update_video_slideshow(self):
        if self.video_paths:
            self.play_next_video()

    def toggle_randomize_videos(self, state):
        self.is_randomized_videos = (state == Qt.Checked)
        if self.is_randomized_videos:
            random.shuffle(self.video_paths)
            self.current_video_index = 0
            self.load_video(self.current_video_index)

    def toggle_video_slideshow(self):
        if self.video_slideshow_active:
            self.video_slideshow_active = False
            self.slideshow_video_button.setText("Start Slideshow")
            self.video_timer.stop()
        else:
            self.video_slideshow_active = True
            self.slideshow_video_button.setText("Stop Slideshow")
            self.update_video_interval()
            self.video_timer.start()

    def update_video_interval(self):
        self.video_slideshow_interval = self.interval_video_spinbox.value()
        if self.video_slideshow_active:
            self.video_timer.setInterval(self.video_slideshow_interval)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            video_extensions = ["*.mp4", "*.avi", "*.mov", "*.mkv"]
            self.video_paths = []
            for ext in video_extensions:
                self.video_paths.extend(glob.glob(os.path.join(directory, ext)))
            if self.video_paths:
                self.current_video_index = 0
                self.load_video(self.current_video_index)
            else:
                QMessageBox.information(self, "No Videos", "No videos found in the selected directory.")

    def handle_state_change(self, state):
        if state == QMediaPlayer.EndOfMedia and self.video_slideshow_active:
            self.update_video_slideshow()

    def handle_error(self):
        QMessageBox.critical(self, "Error", f"An error occurred: {self.mediaPlayer.errorString()}")

class MultiMediaViewer(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        splitter = QSplitter(Qt.Horizontal)
        self.imagePlayer = ImagePlayer()
        self.videoPlayer = VideoPlayer()

        splitter.addWidget(self.imagePlayer)
        splitter.addWidget(self.videoPlayer)

        layout = QVBoxLayout()
        layout.addWidget(splitter)

        self.setLayout(layout)
        self.setWindowTitle("Multi Media Viewer")
        self.resize(1200, 600)

def main():
    app = QApplication(sys.argv)

    viewer = MultiMediaViewer()
    viewer.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
