from PyQt5.QtWidgets import QWidget, QVBoxLayout
from gui.ConfigForm import ConfigForm


class ImagesWidget(QWidget):
    def __init__(self, parent=None):
        super(ImagesWidget, self).__init__(parent=parent)
        self.config_form = ConfigForm(parent=parent)
        self.create_images_grid()
        layout = QVBoxLayout()
        layout.addWidget(self.config_form)

        self.setLayout(layout)

    def create_images_grid(self):
        self.images_grid = QWidget()


