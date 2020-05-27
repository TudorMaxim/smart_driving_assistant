from PyQt5.QtCore import QThreadPool, Qt, QUrl
from PyQt5.QtGui import QMovie
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QGroupBox, QHBoxLayout, QErrorMessage, QPushButton, QStyle, QSlider
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
        self.config_form.browse_button.clicked.connect(self.config_form.browse_video)
        self.config_form.button_box.accepted.connect(self.run_detector)
        self.config_form.button_box.rejected.connect(self.config_form.clear_form)

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
        self.is_running = False
        if self.video_box_layout.count() > 0:
            self.clear_video_box_layout()

        self.video_player_wrapper = QWidget()
        self.wrapper_layout = QVBoxLayout()
        self.wrapper_layout.setContentsMargins(0, 0, 0, 0)

        self.media_player = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.video_player_widget = QVideoWidget()
        self.play_button = QPushButton()
        self.play_button.setEnabled(False)
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.clicked.connect(self.play_video)

        self.position_slider = QSlider(Qt.Horizontal)
        self.position_slider.setRange(0, 0)
        self.position_slider.sliderMoved.connect(self.set_position)

        _, out_paths = self.dataset_utils.load_detections()
        if len(out_paths) > 0:
            self.media_player.setMedia(QMediaContent(QUrl.fromLocalFile(out_paths[0])))
            self.play_button.setEnabled(True)

        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.addWidget(self.play_button)
        control_layout.addWidget(self.position_slider)

        self.wrapper_layout.addWidget(self.video_player_widget)
        self.wrapper_layout.addLayout(control_layout)
        self.video_player_wrapper.setLayout(self.wrapper_layout)
        self.video_box_layout.addWidget(self.video_player_wrapper)
        # self.video_box_layout.addWidget(self.video_player_widget)
        # self.video_box_layout.addLayout(control_layout)

        self.media_player.setVideoOutput(self.video_player_widget)
        self.media_player.stateChanged.connect(self.media_state_changed)
        self.media_player.positionChanged.connect(self.position_changed)
        self.media_player.durationChanged.connect(self.duration_changed)

    def clear_video_box_layout(self):
        self.video_box_layout.itemAt(0).widget().deleteLater()

    def show_loading_spinner(self):
        self.clear_video_box_layout()
        spinner_label = QLabel('Spinner')
        spinner_label.setAlignment(Qt.AlignCenter)
        spinner_movie = QMovie(Constants.SPINNER_PATH)
        spinner_label.setMovie(spinner_movie)
        spinner_movie.start()
        self.video_box_layout.addWidget(spinner_label)

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
        tiny = self.config_form.od_use_tiny_yolo.isChecked()

        worker = VideosWorker(
            confidence_thresh=confidence_thresh,
            nms_thresh=iou_thresh,
            image_size=image_size,
            direction_error=direction_error,
            video_path=self.config_form.path,
            tiny=tiny
        )
        worker.signals.finished.connect(self.create_video_grid)
        worker.signals.error.connect(self.show_error)

        self.show_loading_spinner()
        self.is_running = True
        self.threadpool.start(worker)

    def play_video(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def media_state_changed(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

    def position_changed(self, position):
        self.position_slider.setValue(position)

    def duration_changed(self, duration):
        self.position_slider.setRange(0, duration)

    def set_position(self, position):
        self.media_player.setPosition(position)

    def show_error(self):
        error_dialog = QErrorMessage()
        error_dialog.showMessage('An error occured while processing the video!')


