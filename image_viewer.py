import sys
import os
import random
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QPushButton,
                             QFileDialog, QHBoxLayout, QLineEdit, QCheckBox, QScrollArea, QSizePolicy)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer


class ImageViewer(QWidget):
    def __init__(self, parent=None, remove_callback=None):
        super().__init__(parent)

        self.remove_callback = remove_callback

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(True)
        self.image_label.setMinimumSize(1, 1)

        self.current_image_index = -1
        self.image_files = []
        self.slideshow_running = False

        # Timer for the slideshow
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_image_in_slideshow)

        # Main layout for a single viewer
        layout = QVBoxLayout()

        # Add QLabel to layout
        layout.addWidget(self.image_label)

        # Buttons layout
        button_layout = QHBoxLayout()

        # Previous button
        prev_button = QPushButton('Previous')
        prev_button.clicked.connect(self.show_previous_image)
        button_layout.addWidget(prev_button)

        # Next button
        next_button = QPushButton('Next')
        next_button.clicked.connect(self.show_next_image)
        button_layout.addWidget(next_button)

        # Add buttons layout to main layout
        layout.addLayout(button_layout)

        # Slideshow Button
        self.slideshow_button = QPushButton('Start Slideshow')
        self.slideshow_button.clicked.connect(self.toggle_slideshow)
        layout.addWidget(self.slideshow_button)

        # Interval Input
        interval_layout = QHBoxLayout()
        self.interval_input = QLineEdit(self)
        self.interval_input.setPlaceholderText('Interval (seconds)')
        interval_layout.addWidget(self.interval_input)

        # Random Order Checkbox
        self.random_order_checkbox = QCheckBox("Random Order")
        interval_layout.addWidget(self.random_order_checkbox)

        layout.addLayout(interval_layout)

        # Remove Button
        remove_button = QPushButton('Remove')
        remove_button.clicked.connect(self.remove_self)
        layout.addWidget(remove_button)

        # Set styles for the remove button
        remove_button.setStyleSheet("""
            QPushButton {
                background-color: #ff4c4c;
                color: white;
                padding: 5px 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #ff1c1c;
            }
        """)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Even distribution of space

    def load_images(self, directory):
        # Filter for image files
        supported_formats = (".png", ".jpg", ".jpeg", ".bmp", ".gif")
        self.image_files = [os.path.join(directory, f) for f in os.listdir(directory) if
                            f.lower().endswith(supported_formats)]
        self.current_image_index = 0
        if self.image_files:
            self.show_image(self.current_image_index)

    def show_image(self, index):
        # Display the image at the current index
        if 0 <= index < len(self.image_files):
            pixmap = QPixmap(self.image_files[index])
            scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        if self.image_files and 0 <= self.current_image_index < len(self.image_files):
            self.show_image(self.current_image_index)

    def show_next_image(self):
        if self.image_files:
            self.current_image_index = (self.current_image_index + 1) % len(self.image_files)
            self.show_image(self.current_image_index)

    def show_previous_image(self):
        if self.image_files:
            self.current_image_index = (self.current_image_index - 1) % len(self.image_files)
            self.show_image(self.current_image_index)

    def toggle_slideshow(self):
        if self.slideshow_running:
            self.stop_slideshow()
        else:
            self.start_slideshow()

    def start_slideshow(self):
        try:
            interval = int(self.interval_input.text()) * 1000  # Convert seconds to milliseconds
        except ValueError:
            interval = 2000  # Default to 2 seconds if input is invalid

        if self.image_files:
            self.slideshow_running = True
            self.slideshow_button.setText('Stop Slideshow')
            self.timer.start(interval)

    def stop_slideshow(self):
        self.slideshow_running = False
        self.slideshow_button.setText('Start Slideshow')
        self.timer.stop()

    def next_image_in_slideshow(self):
        if self.random_order_checkbox.isChecked():
            self.current_image_index = random.randint(0, len(self.image_files) - 1)
        else:
            self.current_image_index = (self.current_image_index + 1) % len(self.image_files)

        self.show_image(self.current_image_index)

    def remove_self(self):
        if self.remove_callback:
            self.remove_callback(self)


class MultiDirectoryViewer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Multi-Directory Image Viewer')
        self.setGeometry(100, 100, 1200, 600)

        self.main_layout = QVBoxLayout()

        # Button to load multiple directories
        load_button = QPushButton('Load Directories')
        load_button.clicked.connect(self.load_directories)
        self.main_layout.addWidget(load_button)

        # Set button styles
        load_button.setStyleSheet("""
            QPushButton {
                background-color: #5cb85c;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4cae4c;
            }
        """)

        # Horizontal layout to add multiple ImageViewer widgets
        self.viewer_layout = QHBoxLayout()

        # Scroll Area to handle multiple directories horizontally
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(self.viewer_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        self.main_layout.addWidget(scroll_area)

        self.setLayout(self.main_layout)

        # Apply overall styles
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                color: #ffffff;
            }
            QLabel {
                border: 1px solid #333;
                padding: 5px;
                background-color: #1e1e1e;
                font-family: Arial, sans-serif;
                font-size: 14px;
                color: #ffffff;
            }
            QLineEdit {
                border-radius: 5px;
                border: 1px solid #444;
                padding: 5px;
                background-color: #2c2c2c;
                color: #ffffff;
            }
            QCheckBox {
                font-family: Arial, sans-serif;
                font-size: 12px;
                padding: 5px;
                color: #ffffff;
            }
            QPushButton {
                background-color: #444;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)

    def load_directories(self):
        # Allow user to select multiple directories
        directory = QFileDialog.getExistingDirectory(self, "Select Directory",
                                                     options=QFileDialog.ShowDirsOnly | QFileDialog.DontUseNativeDialog)
        if directory:
            # Add one ImageViewer per directory
            viewer = ImageViewer(remove_callback=self.remove_viewer)
            viewer.load_images(directory)
            self.viewer_layout.addWidget(viewer)

    def remove_viewer(self, viewer):
        # Remove the viewer from the layout and adjust the window
        self.viewer_layout.removeWidget(viewer)
        viewer.deleteLater()

        # Force the layout to adjust sizes after removing a viewer
        self.adjust_layout()

    def adjust_layout(self):
        # Loop through all the viewers and set them to have equal width
        total_viewers = self.viewer_layout.count()
        for i in range(total_viewers):
            widget = self.viewer_layout.itemAt(i).widget()
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            widget.updateGeometry()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewer = MultiDirectoryViewer()
    viewer.show()
    sys.exit(app.exec_())
