from controller.LaneDetectionController import LaneDetectionController
from controller.ObjectDetectionController import ObjectDetectionController
from model.Line import Line


class DrivingAssistantController:
    def __init__(self, root_path='./', confidence_threshold=0.8, nms_threshold=0.4, image_size=416):
        self.lane_detection_controller = LaneDetectionController(root_path=root_path)
        self.object_detection_controller = ObjectDetectionController(
            root_path=root_path,
            confidence_threshold=confidence_threshold,
            nms_threshold=nms_threshold,
            image_size=image_size
        )

    def detect(self, image):
        img = image.copy()
        detections = self.object_detection_controller.detect(img)
        result = self.lane_detection_controller.detect(image)
        return self.object_detection_controller.draw_bounding_boxes(result, detections)

    def reset_lanes(self):
        self.lane_detection_controller.left_line = Line()
        self.lane_detection_controller.right_line = Line()
