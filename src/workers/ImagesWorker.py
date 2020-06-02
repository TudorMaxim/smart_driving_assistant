from PyQt5.QtCore import QRunnable
from controller.DrivingAssistantController import DrivingAssistantController
from gui.WorkerSignals import WorkerSignals
from utils.Constants import Constants


class ImagesWorker(QRunnable):
    def __init__(self, confidence_thresh, nms_thresh, image_size, direction_error, images_path, tiny):
        super(ImagesWorker, self).__init__()
        self.confidence_thresh = confidence_thresh
        self.nsm_thresh = nms_thresh
        self.image_size = image_size
        self.direction_error = direction_error
        self.images_path = images_path
        self.tiny = tiny
        self.signals = WorkerSignals()

    def run(self) -> None:
        try:
            driving_assistant_controller = DrivingAssistantController(
                confidence_threshold=self.confidence_thresh,
                nms_threshold=self.nsm_thresh,
                direction_error=self.direction_error,
                image_size=self.image_size,
                tiny=self.tiny
            )
            driving_assistant_controller.detect_on_images(images_path=self.images_path)
            self.signals.finished.emit()
        except:
            self.signals.error.emit()
