from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QListWidget, QStackedWidget

from gui.HeaderWidget import HeaderWidget
from gui.ImagesWidget import ImagesWidget
from gui.VideosWidget import VideosWidget


class MainWidget(QWidget):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent=parent)
        self.setWindowTitle("Smart Driving Assistant")
        self.setMinimumSize(640, 360)
        self.setWindowIcon(QIcon('./assets/logo.jpg'))
        # header
        self.header = HeaderWidget()
        self.header.currentRowChanged.connect(self.display)

        self.images_widget = ImagesWidget(parent=self)
        self.videos_widget = VideosWidget(parent=self)

        self.stack = QStackedWidget(parent=self)
        self.stack.addWidget(self.images_widget)
        self.stack.addWidget(self.videos_widget)

        layout = QVBoxLayout(self)
        layout.addWidget(self.header)
        layout.addWidget(self.stack)
        layout.addWidget(self.header)
        layout.addWidget(self.stack)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def display(self, index):
        self.stack.setCurrentIndex(index)
