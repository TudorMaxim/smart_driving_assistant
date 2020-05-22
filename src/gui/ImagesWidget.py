from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QGridLayout, QLabel, QScrollArea, QHBoxLayout

from controller.DrivingAssistantController import DrivingAssistantController
from gui.ConfigForm import ConfigForm
from utils.Constants import Constants
from utils.DatasetUtils import DatasetUtils


class ImagesWidget(QWidget):
    def __init__(self, parent=None):
        super(ImagesWidget, self).__init__(parent=parent)
        self.is_running = False
        self.dataset_utils = DatasetUtils(detections_path=Constants.DETECTIONS_PATH)
        self.config_form = ConfigForm(parent=parent)
        self.config_form.button_box.accepted.connect(self.run_detector)
        self.config_form.button_box.rejected.connect(self.reset_fields)

        self.images_grid = QGroupBox("Results")
        self.images_box_layout = QVBoxLayout()
        self.create_images_grid()
        self.images_grid.setLayout(self.images_box_layout)

        layout = QHBoxLayout()
        layout.addWidget(self.config_form)
        layout.addWidget(self.images_grid)
        self.setLayout(layout)
        self.setStyleSheet(open(Constants.STYLES_PATH + 'ImagesWidget.css').read())

    def create_images_grid(self):
        images_scroll_area = QScrollArea()
        images_scroll_area_layout = QVBoxLayout()
        _, out_paths = self.dataset_utils.load_detections()
        print('Recreating results widget')
        print(out_paths)
        for out_path in out_paths:
            result = QLabel('Result Image')
            result.setPixmap(QPixmap(out_path).scaledToHeight(720))
            # layout = QHBoxLayout()
            # layout.addWidget(result)
            # wrapper = QWidget()
            # wrapper.setLayout(layout)
            images_scroll_area_layout.addWidget(result)

        images_widget = QWidget()
        images_widget.setLayout(images_scroll_area_layout)
        images_scroll_area.setWidget(images_widget)
        self.images_box_layout.addWidget(images_scroll_area)


    def clear_images_grid(self):
        for i in reversed(range(self.images_box_layout.count())):
            self.images_box_layout.itemAt(i).widget().deleteLater()

    def run_detector(self):
        if self.is_running:
            return
        if self.config_form.path == '':
            self.config_form.error_message.setText('Please select an images folder')
            return
        self.clear_images_grid()
        confidence_thresh = int(self.config_form.od_confidence_thresh_input.text()) / 100
        iou_thresh = int(self.config_form.od_iou_thresh_input.text()) / 100
        direction_error = int(self.config_form.ld_direction_error_input.text())
        controller = DrivingAssistantController(
            root_path=Constants.ROOT_PATH,
            confidence_threshold=confidence_thresh,
            nms_threshold=iou_thresh,
            direction_error=direction_error
        )
        self.is_running = True
        print('Running detector')
        controller.detect_on_images(self.config_form.path)
        self.is_running = False
        print('Finished')
        self.create_images_grid()

    def reset_fields(self):
        self.config_form.path = ''
        self.config_form.selected_path.setText(self.config_form.path)
        self.config_form.error_message.setText('')
        self.config_form.ld_direction_error_input.setValue(15)
        self.config_form.od_iou_thresh_input.setValue(40)
        self.config_form.od_confidence_thresh_input.setValue(50)
        self.config_form.image_size_input.setCurrentIndex(1)

