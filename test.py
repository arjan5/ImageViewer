import sys
import os
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget, QLabel, \
    QHBoxLayout, QSplitter, QCheckBox, QSpinBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt
from PIL import Image as PILImage
import random


class MediaViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Viewer")
        self.setGeometry(100, 100, 1200, 600)

        # Create main layout and splitter
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        self.splitter = QSplitter(Qt.Horizontal)
        self.main_layout.addWidget(self.splitter)

        # Image widget and layout
        self.image_widget = QWidget()
        self.image_layout = QVBoxLayout(self.image_widget)

        self.prev_image_button = QPushButton("Previous Image")
        self.prev_image_button.clicked.connect(self.prev_image)
        self.next_image_button = QPushButton("Next Image")
        self.next_image_button.clicked.connect(self.next_image)
        self.randomize_images_checkbox = QCheckBox("Randomize Images")
        self.randomize_images_checkbox.stateChanged.connect(self.toggle_randomize_images)
        self.slideshow_button = QPushButton("Start Slideshow")
        self.slideshow_button.clicked.connect(self.toggle_slideshow)
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(100, 10000)  # Interval range from 100ms to 10s
        self.interval_spinbox.setValue(1000)  # Default to 1 second
        self.interval_spinbox.setSuffix(" ms")
        self.interval_spinbox.valueChanged.connect(self.update_interval)

        self.image_layout.addWidget(self.prev_image_button)
        self.image_layout.addWidget(self.next_image_button)
        self.image_layout.addWidget(self.randomize_images_checkbox)
        self.image_layout.addWidget(self.slideshow_button)
        self.image_layout.addWidget(self.interval_spinbox)

        self.image_label = QLabel()
        self.image_label.setScaledContents(True)  # Ensure the image scales with the label
        self.image_layout.addWidget(self.image_label)

        # Video widget and layout
        self.video_widget = QWidget()
        self.video_layout = QVBoxLayout(self.video_widget)

        self.prev_video_button = QPushButton("Previous Video")
        self.prev_video_button.clicked.connect(self.prev_video)
        self.next_video_button = QPushButton("Next Video")
        self.next_video_button.clicked.connect(self.next_video)
        self.randomize_videos_checkbox = QCheckBox("Randomize Videos")
        self.randomize_videos_checkbox.stateChanged.connect(self.toggle_randomize_videos)
        self.slideshow_video_button = QPushButton("Start Slideshow")
        self.slideshow_video_button.clicked.connect(self.toggle_video_slideshow)

        self.interval_video_spinbox = QSpinBox()
        self.interval_video_spinbox.setRange(100, 10000)  # Interval range from 100ms to 10s
        self.interval_video_spinbox.setValue(1000)  # Default to 1 second
        self.interval_video_spinbox.setSuffix(" ms")
        self.interval_video_spinbox.valueChanged.connect(self.update_video_interval)

        self.video_layout.addWidget(self.prev_video_button)
        self.video_layout.addWidget(self.next_video_button)
        self.video_layout.addWidget(self.randomize_videos_checkbox)
        self.video_layout.addWidget(self.slideshow_video_button)
        self.video_layout.addWidget(self.interval_video_spinbox)

        self.video_label = QLabel()
        self.video_label.setScaledContents(True)  # Ensure the video scales with the label
        self.video_layout.addWidget(self.video_label)

        # Add widgets to splitter
        self.splitter.addWidget(self.image_widget)
        self.splitter.addWidget(self.video_widget)

        # Set equal sizes
        self.splitter.setSizes([self.width() // 2, self.width() // 2])

        self.image_files = []
        self.video_files = []
        self.current_image_index = 0
        self.current_video_index = 0
        self.is_randomized_images = False
        self.is_randomized_videos = False
        self.slideshow_active = False
        self.video_slideshow_active = False
        self.slideshow_interval = 1000
        self.video_slideshow_interval = 1000

        self.image_timer = QTimer()
        self.image_timer.timeout.connect(self.update_image)
        self.video_timer = QTimer()
        self.video_timer.timeout.connect(self.update_video)

        self.loop_video_checkbox = QCheckBox("Loop Video")
        self.video_layout.addWidget(self.loop_video_checkbox)

        self.restart_video_button = QPushButton("Restart Video")
        self.restart_video_button.clicked.connect(self.restart_video)
        self.video_layout.addWidget(self.restart_video_button)

        self.load_directories()

    def load_directories(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.Directory)
        file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        file_dialog.setViewMode(QFileDialog.List)
        file_dialog.setWindowTitle("Select Directories (Hold Ctrl for multiple)")
        if file_dialog.exec_():
            dirs = file_dialog.selectedFiles()
            for directory in dirs:
                for file_name in os.listdir(directory):
                    file_path = os.path.join(directory, file_name)
                    if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                        self.image_files.append(file_path)
                    elif file_path.lower().endswith(('.mp4', '.webm', '.gif')):
                        self.video_files.append(file_path)

        self.image_files.sort()
        self.video_files.sort()

        print(f"Loaded image files: {self.image_files}")
        print(f"Loaded video files: {self.video_files}")

        if self.image_files:
            self.show_image(0)
        if self.video_files:
            self.show_video(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_image()
        self.update_video()

    def show_image(self, index):
        if not self.image_files:
            print("No image files available.")
            return

        if self.is_randomized_images:
            self.image_files = random.sample(self.image_files, len(self.image_files))
            self.current_image_index = 0

        if index < 0:
            index = len(self.image_files) - 1
        elif index >= len(self.image_files):
            index = 0

        file_path = self.image_files[index]
        image = PILImage.open(file_path)
        img_width, img_height = image.size

        # Resize image to fit within the image label
        widget_width = self.image_label.width()
        widget_height = self.image_label.height()
        img_ratio = img_width / img_height
        widget_ratio = widget_width / widget_height

        if img_ratio > widget_ratio:
            new_width = widget_width
            new_height = int(new_width / img_ratio)
        else:
            new_height = widget_height
            new_width = int(new_height * img_ratio)

        image = image.resize((new_width, new_height), PILImage.Resampling.LANCZOS)
        qt_image = QImage(np.array(image), image.width, image.height, image.width * 3, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)

        self.image_label.setPixmap(pixmap)
        self.current_image_index = index

    def show_video(self, index):
        if not self.video_files:
            print("No video files available.")
            return

        if index < 0:
            index = len(self.video_files) - 1
        elif index >= len(self.video_files):
            index = 0

        file_path = self.video_files[index]

        # Release previous video capture if it exists
        if hasattr(self, 'cap'):
            self.cap.release()

        self.cap = cv2.VideoCapture(file_path)
        if not self.cap.isOpened():
            print(f"Error: Unable to open video file {file_path}")
            return

        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        if self.fps <= 0:
            print("Invalid FPS detected, setting to default 30 FPS.")
            self.fps = 30  # Default FPS
        else:
            print(f"Video FPS: {self.fps}")

        self.video_timer.start(int(1000 / self.fps))

        self.current_video_index = index

    def update_image(self):
        if self.slideshow_active:
            self.next_image()

    def update_video(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                qt_image = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_image)

                # Resize video to fit within the video label
                widget_width = self.video_label.width()
                widget_height = self.video_label.height()
                frame_width = pixmap.width()
                frame_height = pixmap.height()
                frame_ratio = frame_width / frame_height
                widget_ratio = widget_width / widget_height

                if frame_ratio > widget_ratio:
                    new_width = widget_width
                    new_height = int(new_width / frame_ratio)
                else:
                    new_height = widget_height
                    new_width = int(new_height * frame_ratio)

                pixmap = pixmap.scaled(new_width, new_height, Qt.KeepAspectRatio)
                self.video_label.setPixmap(pixmap)
            else:
                print("End of video reached.")
                if self.loop_video_checkbox.isChecked():
                    print("Looping video...")
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart video
                else:
                    self.cap.release()
                    self.video_timer.stop()

                    if self.video_slideshow_active:
                        QTimer.singleShot(1000, self.next_video)
                    else:
                        print("Video ends without slideshow.")

    def prev_image(self):
        self.current_image_index = (self.current_image_index - 1) % len(self.image_files)
        self.show_image(self.current_image_index)

    def next_image(self):
        self.current_image_index = (self.current_image_index + 1) % len(self.image_files)
        self.show_image(self.current_image_index)

    def prev_video(self):
        self.current_video_index = (self.current_video_index - 1) % len(self.video_files)
        self.show_video(self.current_video_index)

    def next_video(self):
        self.current_video_index = (self.current_video_index + 1) % len(self.video_files)
        self.show_video(self.current_video_index)

    def toggle_randomize_images(self, state):
        self.is_randomized_images = (state == Qt.Checked)
        if self.is_randomized_images:
            random.shuffle(self.image_files)
            self.current_image_index = 0
            self.show_image(self.current_image_index)

    def toggle_randomize_videos(self, state):
        self.is_randomized_videos = (state == Qt.Checked)
        if self.is_randomized_videos:
            random.shuffle(self.video_files)
            self.current_video_index = 0
            self.show_video(self.current_video_index)

    def toggle_slideshow(self):
        if self.slideshow_active:
            self.slideshow_active = False
            self.slideshow_button.setText("Start Slideshow")
            self.image_timer.stop()
        else:
            self.slideshow_active = True
            self.slideshow_button.setText("Stop Slideshow")
            self.update_interval()
            self.image_timer.start(self.slideshow_interval)

    def toggle_video_slideshow(self):
        if self.video_slideshow_active:
            self.video_slideshow_active = False
            self.slideshow_video_button.setText("Start Slideshow")
            self.video_timer.stop()
        else:
            self.video_slideshow_active = True
            self.slideshow_video_button.setText("Stop Slideshow")
            self.update_video_interval()
            self.show_video(self.current_video_index)
            self.video_timer.start(int(1000 / self.fps))

    def update_interval(self):
        self.slideshow_interval = self.interval_spinbox.value()
        if self.slideshow_active:
            self.image_timer.start(self.slideshow_interval)

    def update_video_interval(self):
        self.video_slideshow_interval = self.interval_video_spinbox.value()
        if self.video_slideshow_active:
            self.video_timer.start(self.video_slideshow_interval)

    def restart_video(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            # Reset the video to the beginning
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.video_timer.start(int(1000 / self.fps))  # Restart video playback
            print("Video restarted.")
        else:
            print("No video is currently playing.")
            if self.video_files:
                # If no video is currently playing, restart the current video manually
                self.show_video(self.current_video_index)
                print("Current video restarted.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = MediaViewer()
    viewer.show()
    sys.exit(app.exec_())
