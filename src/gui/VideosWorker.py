from PyQt5.QtCore import QRunnable
from controller.DrivingAssistantController import DrivingAssistantController
from gui.WorkerSignals import WorkerSignals
from utils.Constants import Constants


class VideosWorker(QRunnable):
    def __init__(self, confidence_thresh, nms_thresh, image_size, direction_error, video_path):
        super(VideosWorker, self).__init__()
        self.confidence_thresh = confidence_thresh
        self.nsm_thresh = nms_thresh
        self.image_size = image_size
        self.direction_error = direction_error
        self.video_path = video_path
        self.signals = WorkerSignals()

    def run(self) -> None:
        try:
            driving_assistant_controller = DrivingAssistantController(
                root_path=Constants.ROOT_PATH,
                confidence_threshold=self.confidence_thresh,
                nms_threshold=self.nsm_thresh,
                direction_error=self.direction_error,
                image_size=self.image_size
            )
            driving_assistant_controller.detect_on_video(video_in_path=self.video_path)
            self.signals.finished.emit()
        except:
            self.signals.error.emit()