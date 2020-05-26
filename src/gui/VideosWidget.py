from PyQt5.QtCore import QThreadPool, Qt
from PyQt5.QtGui import QMovie, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QGroupBox, QHBoxLayout, QScrollArea, QErrorMessage
from gui.ConfigForm import ConfigForm
from gui.VideosWorker import VideosWorker
from utils.Constants import Constants
from utils.DatasetUtils import DatasetUtils


class VideosWidget(QWidget):
    def __init__(self, parent=None):
        super(VideosWidget, self).__init__(parent=parent)
        self.is_running = False
        self.threadpool = QThreadPool()

        self.dataset_utils = DatasetUtils(detections_path=Constants.VIDEO_DETECTIONS_PATH)
        self.config_form = ConfigForm(parent=parent)
        self.config_form.button_box.accepted.connect(self.run_detector)
        self.config_form.button_box.rejected.connect(self.reset_fields)

        self.video_grid = QGroupBox("Results")
        self.video_box_layout = QVBoxLayout()
        self.create_video_grid()
        self.video_grid.setLayout(self.video_box_layout)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.config_form)
        self.layout.addWidget(self.video_grid)
        self.setLayout(self.layout)
        # self.setStyleSheet(open(Constants.STYLES_PATH + 'ImagesWidget.css').read())

    def create_video_grid(self):
        pass
        # if self.video_box_layout.count() > 0:
        #     self.clear_video_box_layout()
        #
        # self.is_running = False
        # video_scroll_area = QScrollArea()
        # # video_scroll_area.horizontalScrollBar().setEnabled(False)
        # video_scroll_area.setWidgetResizable(True)
        # video_scroll_area_layout = QVBoxLayout()
        # video_scroll_area_layout.setContentsMargins(0, 0, 0, 0)
        # _, out_paths = self.dataset_utils.load_detections()
        #
        # for out_path in out_paths:
        #     result = QLabel('Result Image')
        #     result.setAlignment(Qt.AlignCenter)
        #     # result.setScaledContents(True)
        #     result.setPixmap(QPixmap(out_path))
        #     video_scroll_area_layout.addWidget(result)
        #
        # video_widget = QWidget()
        # video_widget.setLayout(video_scroll_area_layout)
        # video_scroll_area.setWidget(video_widget)
        # self.video_box_layout.addWidget(video_scroll_area)

    def show_loading_spinner(self):
        self.clear_video_box_layout()
        spinner_label = QLabel('Spinner')
        spinner_label.setAlignment(Qt.AlignCenter)
        spinner_movie = QMovie(Constants.SPINNER_PATH)
        spinner_label.setMovie(spinner_movie)
        spinner_movie.start()
        self.video_box_layout.addWidget(spinner_label)

    def clear_video_box_layout(self):
        for i in reversed(range(self.video_box_layout.count())):
            self.video_box_layout.itemAt(i).widget().deleteLater()

    def run_detector(self):
        if self.is_running:
            return
        if self.config_form.path == '':
            self.config_form.error_message.setText('Please select a video')
            return
        img_sizes = [256, 416, 720]
        confidence_thresh = int(self.config_form.od_confidence_thresh_input.text()) / 100
        iou_thresh = int(self.config_form.od_iou_thresh_input.text()) / 100
        direction_error = int(self.config_form.ld_direction_error_input.text())
        image_size = img_sizes[self.config_form.image_size_input.currentIndex()]

        worker = VideosWorker(
            confidence_thresh=confidence_thresh,
            nms_thresh=iou_thresh,
            image_size=image_size,
            direction_error=direction_error,
            video_path=self.config_form.path
        )
        worker.signals.finished.connect(self.create_video_grid)
        worker.signals.error.connect(self.show_error)

        self.show_loading_spinner()
        self.is_running = True
        self.threadpool.start(worker)

    def show_error(self):
        error_dialog = QErrorMessage()
        error_dialog.showMessage('An error occured while processing the video!')

    def reset_fields(self):
        self.config_form.path = ''
        self.config_form.selected_path.setText(self.config_form.path)
        self.config_form.error_message.setText('')
        self.config_form.ld_direction_error_input.setValue(15)
        self.config_form.od_iou_thresh_input.setValue(40)
        self.config_form.od_confidence_thresh_input.setValue(50)
        self.config_form.image_size_input.setCurrentIndex(1)

