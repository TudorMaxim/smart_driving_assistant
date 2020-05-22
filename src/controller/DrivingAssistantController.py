import cv2
from moviepy.video.io.VideoFileClip import VideoFileClip

from controller.LaneDetectionController import LaneDetectionController
from controller.ObjectDetectionController import ObjectDetectionController
from model.Line import Line
from utils.Constants import Constants
from utils.DatasetUtils import DatasetUtils


class DrivingAssistantController:
    def __init__(self, root_path='./', confidence_threshold=0.8, nms_threshold=0.4, image_size=416, direction_error=15):
        self.lane_detection_controller = LaneDetectionController(
            root_path=root_path,
            direction_error=direction_error
        )
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

    def detect_on_images(self, images_path=Constants.IMAGES_IN_PATH):
        dataset_utils = DatasetUtils(detections_path=Constants.DETECTIONS_PATH)
        paths, images = dataset_utils.get_images_from_directory(images_path)
        out_paths = []
        print("Loaded images.")
        for image, path in zip(images, paths):
            self.reset_lanes()
            result = self.detect(image)
            filename = path.split("/")[-1]
            out_paths.append(Constants.IMAGES_OUT_PATH + filename)
            cv2.imwrite(Constants.IMAGES_OUT_PATH + filename, result)
        print('Detections saved.')
        dataset_utils.save_detections(paths, out_paths)

    def detect_on_video(self, video_in_path=Constants.VIDEOS_IN_PATH):
        video = VideoFileClip(video_in_path)
        output_video = video.fl_image(self.detect)
        output_video.write_videofile(Constants.VIDEOS_OUT_PATH, audio=False)
