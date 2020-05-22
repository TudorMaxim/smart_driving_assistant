from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QGridLayout, QLabel, QScrollArea, QHBoxLayout
from gui.ConfigForm import ConfigForm
from utils.Constants import Constants
from utils.DatasetUtils import DatasetUtils


class ImagesWidget(QWidget):
    def __init__(self, parent=None):
        super(ImagesWidget, self).__init__(parent=parent)
        self.dataset_utils = DatasetUtils(detections_path=Constants.DETECTIONS_PATH)
        _, self.out_paths = self.dataset_utils.load_detections()
        self.config_form = ConfigForm(parent=parent)
        self.create_images_grid()
        layout = QHBoxLayout()
        layout.addWidget(self.config_form)
        layout.addWidget(self.images_grid)
        self.setLayout(layout)
        self.setStyleSheet(open(Constants.STYLES_PATH + 'ImagesWidget.css').read())

    def create_images_grid(self):
        self.images_grid = QGroupBox("Results")
        images_box_layout = QVBoxLayout()
        images_scroll_area = QScrollArea()
        images_scroll_area_layout = QVBoxLayout()

        for out_path in self.out_paths:
            result = QLabel('Result Image')
            result.setPixmap(QPixmap(out_path).scaledToHeight(720))
            layout = QHBoxLayout()
            layout.addWidget(result)
            wrapper = QWidget()
            wrapper.setLayout(layout)
            images_scroll_area_layout.addWidget(wrapper)

        images_widget = QWidget()
        images_widget.setLayout(images_scroll_area_layout)
        images_scroll_area.setWidget(images_widget)
        images_box_layout.addWidget(images_scroll_area)
        self.images_grid.setLayout(images_box_layout)


