from PyQt5.QtWidgets import QListWidget
from utils.Constants import Constants


class HeaderWidget(QListWidget):
    def __init__(self, parent=None):
        super(HeaderWidget, self).__init__(parent=parent)
        self.insertItem(0, 'Images')
        self.insertItem(1, 'Videos')
        self.setCurrentRow(0)
        self.setFlow(QListWidget.LeftToRight)
        self.setStyleSheet(open(Constants.STYLES_PATH + 'HeaderWidget.css').read())
