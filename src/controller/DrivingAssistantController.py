import cv2
from moviepy.video.io.VideoFileClip import VideoFileClip
from controller.LaneDetectionController import LaneDetectionController
from controller.ObjectDetectionController import ObjectDetectionController
from model.Line import Line
from utils.Constants import Constants
from utils.DatasetUtils import DatasetUtils


class DrivingAssistantController:
    def __init__(self, confidence_threshold=0.8, nms_threshold=0.4, image_size=416, direction_error=15, tiny=False, plot=False):
        self.lane_detection_controller = LaneDetectionController(
            direction_error=direction_error,
            plot=plot
        )
        self.object_detection_controller = ObjectDetectionController(
            confidence_threshold=confidence_threshold,
            nms_threshold=nms_threshold,
            image_size=image_size,
            tiny=tiny
        )

    def detect(self, image):
        img = image.copy()
        detections = self.object_detection_controller.detect(img)
        result = self.lane_detection_controller.detect(image)
        return self.object_detection_controller.draw_bounding_boxes(result, detections)

    def __reset_lanes(self):
        self.lane_detection_controller.left_line = Line()
        self.lane_detection_controller.right_line = Line()

    def detect_on_images(self, images_path=Constants.IMAGES_IN_PATH):
        dataset_utils = DatasetUtils(detections_path=Constants.DETECTIONS_PATH)
        paths, images = dataset_utils.get_images_from_directory(images_path)
        out_paths = []
        print("Loaded images.")
        for image, path in zip(images, paths):
            self.__reset_lanes()
            result = self.detect(image)
            filename = path.split("/")[-1]
            out_paths.append(Constants.IMAGES_OUT_PATH + filename)
            cv2.imwrite(Constants.IMAGES_OUT_PATH + filename, result)
        print('Detections saved.')
        dataset_utils.save_detections(paths, out_paths)

    def detect_on_video(self, video_in_path=Constants.VIDEOS_IN_PATH):
        dataset_utils = DatasetUtils(detections_path=Constants.VIDEO_DETECTIONS_PATH)
        video = VideoFileClip(video_in_path)
        output_video = video.fl_image(self.detect)
        extension = video_in_path.split(".")[-1]
        filename = video_in_path.split('/')[-1].split('.')[0]
        filename = filename + "_result." + extension
        video_out_path = Constants.VIDEOS_OUT_PATH + filename
        output_video.write_videofile(video_out_path, audio=False)
        dataset_utils.save_detections(in_paths=[video_in_path], out_paths=[video_out_path])
