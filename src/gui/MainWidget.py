from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget
from gui.HeaderWidget import HeaderWidget
from gui.ImagesWidget import ImagesWidget
from gui.VideosWidget import VideosWidget
from utils.Constants import Constants


class MainWidget(QWidget):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent=parent)
        self.setWindowTitle("Smart Driving Assistant")
        self.setMinimumWidth(1024)
        self.setMinimumHeight(550)
        self.setWindowIcon(QIcon(Constants.LOGO_PATH))
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
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        self.setStyleSheet(open(Constants.STYLES_PATH + "MainWidget.css").read())

    def display(self, index):
        self.stack.setCurrentIndex(index)
