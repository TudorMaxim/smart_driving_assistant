import cv2
from moviepy.video.io.VideoFileClip import VideoFileClip

from controller.DrivingAssistantController import DrivingAssistantController
from utils.DatasetUtils import DatasetUtils

IMAGES_IN_PATH = '../input/images/'
IMAGES_OUT_PATH = '../results/images/'
VIDEOS_IN_PATH = '../input/videos/project_video.mp4'
VIDEOS_OUT_PATH = '../results/videos/project_video_result.mp4'
DETECTIONS_PATH = '../config/detections.txt'

controller = DrivingAssistantController(
    root_path='../'
)


def detect_on_images():
    dataset_utils = DatasetUtils(detections_path=DETECTIONS_PATH)
    paths, images = dataset_utils.get_images_from_directory(IMAGES_IN_PATH)
    out_paths = []
    for image, path in zip(images, paths):
        controller.reset_lanes()
        result = controller.detect(image)
        filename = path.split("/")[-1]
        out_paths.append(IMAGES_OUT_PATH + filename)
        cv2.imwrite(IMAGES_OUT_PATH + filename, result)
    dataset_utils.save_detections(paths, out_paths)


def detect_on_video():
    video = VideoFileClip(VIDEOS_IN_PATH)
    output_video = video.fl_image(controller.detect)
    output_video.write_videofile(VIDEOS_OUT_PATH, audio=False)


if __name__ == '__main__':
    detect_on_images()
    # detect_on_video()
