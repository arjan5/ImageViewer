import sys
import os
import glob
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSlider, QFileDialog, QMessageBox, QSpinBox, QCheckBox, QGridLayout
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget

class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.video_paths = []
        self.current_video_index = 0
        self.is_randomized_videos = False
        self.video_slideshow_active = False
        self.video_slideshow_interval = 1000
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self.update_video_slideshow)

        self.init_ui()

    def init_ui(self):
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()

        self.playButton = QPushButton()
        self.playButton.setIcon(QIcon.fromTheme("media-playback-start"))
        self.playButton.clicked.connect(self.play_pause)

        self.prevButton = QPushButton("<< 10s")
        self.prevButton.clicked.connect(self.skip_back)

        self.nextButton = QPushButton("10s >>")
        self.nextButton.clicked.connect(self.skip_forward)

        self.randomize_videos_checkbox = QCheckBox("Randomize Videos")
        self.randomize_videos_checkbox.stateChanged.connect(self.toggle_randomize_videos)

        self.slideshow_video_button = QPushButton("Start Slideshow")
        self.slideshow_video_button.clicked.connect(self.toggle_video_slideshow)

        self.interval_video_spinbox = QSpinBox()
        self.interval_video_spinbox.setRange(100, 10000)  # Interval range from 100ms to 10s
        self.interval_video_spinbox.setValue(1000)  # Default to 1 second
        self.interval_video_spinbox.setSuffix(" ms")
        self.interval_video_spinbox.valueChanged.connect(self.update_video_interval)

        self.scrubBar = QSlider(Qt.Horizontal)
        self.scrubBar.sliderMoved.connect(self.set_position)

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
        layout.addWidget(self.scrubBar)

        self.setLayout(layout)

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.positionChanged.connect(self.position_changed)
        self.mediaPlayer.durationChanged.connect(self.duration_changed)

    def load_video(self, index):
        if self.video_paths:
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(self.video_paths[index])))
            self.play_pause()

    def play_pause(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
            self.playButton.setIcon(QIcon.fromTheme("media-playback-start"))
        else:
            self.mediaPlayer.play()
            self.playButton.setIcon(QIcon.fromTheme("media-playback-pause"))

    def skip_back(self):
        self.mediaPlayer.setPosition(max(0, self.mediaPlayer.position() - 10000))  # Skip back 10 seconds

    def skip_forward(self):
        self.mediaPlayer.setPosition(self.mediaPlayer.position() + 10000)  # Skip forward 10 seconds

    def set_position(self, position):
        self.mediaPlayer.setPosition(position)

    def position_changed(self, position):
        self.scrubBar.setValue(position)

    def duration_changed(self, duration):
        self.scrubBar.setRange(0, duration)

    def play_last_video(self):
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
            self.video_timer.start(self.video_slideshow_interval)

    def update_video_interval(self):
        self.video_slideshow_interval = self.interval_video_spinbox.value()
        if self.video_slideshow_active:
            self.video_timer.start(self.video_slideshow_interval)

    def update_video_slideshow(self):
        if self.video_slideshow_active:
            self.play_next_video()

    def select_directory(self):
        video_dir = QFileDialog.getExistingDirectory(self, "Select Video Directory")
        if video_dir:
            video_extensions = ["*.mp4", "*.avi", "*.mov", "*.mkv", "*.webm", "*.gif"]
            self.video_paths = []
            for ext in video_extensions:
                self.video_paths.extend(glob.glob(os.path.join(video_dir, ext)))
            if self.video_paths:
                self.current_video_index = 0
                self.load_video(self.current_video_index)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Confirm Exit', 'Are you sure you want to exit?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.mediaPlayer.stop()
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = VideoPlayer()
    viewer.show()
    sys.exit(app.exec_())
