from PyQt5.QtCore import QThreadPool, Qt
from PyQt5.QtGui import QPixmap, QMovie
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel, QScrollArea, QHBoxLayout, QErrorMessage
from gui.ConfigForm import ConfigForm
from gui.ImagesWorker import ImagesWorker
from utils.Constants import Constants
from utils.DatasetUtils import DatasetUtils


class ImagesWidget(QWidget):
    def __init__(self, parent=None):
        super(ImagesWidget, self).__init__(parent=parent)
        self.is_running = False
        self.result_images = []
        self.threadpool = QThreadPool()

        self.dataset_utils = DatasetUtils(detections_path=Constants.DETECTIONS_PATH)
        self.config_form = ConfigForm(parent=parent)
        self.config_form.browse_button.clicked.connect(self.config_form.browse)
        self.config_form.button_box.accepted.connect(self.run_detector)
        self.config_form.button_box.rejected.connect(self.config_form.clear_form)

        self.images_grid = QGroupBox("Results")
        self.images_box_layout = QVBoxLayout()
        self.create_images_grid()
        self.images_grid.setLayout(self.images_box_layout)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.config_form)
        self.layout.addWidget(self.images_grid)
        self.setLayout(self.layout)
        self.setStyleSheet(open(Constants.STYLES_PATH + 'ImagesWidget.css').read())

    def create_images_grid(self):
        if self.images_box_layout.count() > 0:
            self.clear_images_box_layout()

        self.is_running = False
        images_scroll_area = QScrollArea()
        images_scroll_area.setWidgetResizable(True)
        self.images_scroll_area_layout = QVBoxLayout()
        self.images_scroll_area_layout.setContentsMargins(0, 0, 0, 0)
        _, out_paths = self.dataset_utils.load_detections()

        min_width = 600
        max_width = 1280
        width = min(max_width, max(min_width, self.images_box_layout.geometry().width() - 48))

        for out_path in out_paths:
            result = QLabel('Result Image')
            result.setAlignment(Qt.AlignCenter)
            pixmap = QPixmap(out_path)
            result.setPixmap(pixmap.scaledToWidth(width))
            self.images_scroll_area_layout.addWidget(result)
            self.result_images.append((result, pixmap))

        images_widget = QWidget()
        images_widget.setLayout(self.images_scroll_area_layout)
        images_scroll_area.setWidget(images_widget)
        self.images_box_layout.addWidget(images_scroll_area)

    def show_loading_spinner(self):
        self.clear_images_box_layout()
        spinner_label = QLabel('Spinner')
        spinner_label.setAlignment(Qt.AlignCenter)
        spinner_movie = QMovie(Constants.SPINNER_PATH)
        spinner_label.setMovie(spinner_movie)
        spinner_movie.start()
        self.images_box_layout.addWidget(spinner_label)

    def clear_images_box_layout(self):
        for i in reversed(range(self.images_box_layout.count())):
            self.images_box_layout.itemAt(i).widget().deleteLater()
        self.result_images.clear()

    def run_detector(self):
        if self.is_running:
            return
        if self.config_form.path == '':
            self.config_form.error_message.setText('Please select the images.')
            return
        img_sizes = [256, 416, 720]
        confidence_thresh = int(self.config_form.od_confidence_thresh_input.text()) / 100
        iou_thresh = int(self.config_form.od_iou_thresh_input.text()) / 100
        direction_error = int(self.config_form.ld_direction_error_input.text())
        image_size = img_sizes[self.config_form.image_size_input.currentIndex()]
        use_tiny_yolo = self.config_form.od_use_tiny_yolo.isChecked()

        worker = ImagesWorker(
            confidence_thresh=confidence_thresh,
            nms_thresh=iou_thresh,
            image_size=image_size,
            direction_error=direction_error,
            images_path=self.config_form.path,
            tiny=use_tiny_yolo
        )
        worker.signals.finished.connect(self.create_images_grid)
        worker.signals.error.connect(self.show_error)

        self.show_loading_spinner()
        self.is_running = True
        self.threadpool.start(worker)

    def show_error(self):
        error_dialog = QErrorMessage()
        error_dialog.showMessage('An error occured while processing the images!')

    def resizeEvent(self, event):
        min_width = 600
        max_width = 1280
        width = min(max_width, max(min_width, self.images_box_layout.geometry().width() - 48))
        for label, pixmap in self.result_images:
            label.setPixmap(pixmap.scaledToWidth(width))
        super(ImagesWidget, self).resizeEvent(event)
