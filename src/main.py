import glob

import cv2
from moviepy.video.io.VideoFileClip import VideoFileClip

from controller.DrivingAssistantController import DrivingAssistantController

IMAGES_IN_PATH = 'assets/images/test*'
IMAGES_OUT_PATH = 'output/images/'
VIDEOS_IN_PATH = 'assets/videos/project_video.mp4'
VIDEOS_OUT_PATH = 'output/videos/project_video_result.mp4'

controller = DrivingAssistantController()


def detect_on_images():
    paths = glob.glob(IMAGES_IN_PATH)
    images = [cv2.imread(path) for path in paths]
    for image, path in zip(images, paths):
        controller.reset_lanes()
        result = controller.detect(image)
        filename = path.split("\\")[-1]
        cv2.imwrite(IMAGES_OUT_PATH + filename, result)


def detect_on_video():
    video = VideoFileClip(VIDEOS_IN_PATH)
    output_video = video.fl_image(controller.detect)
    output_video.write_videofile(VIDEOS_OUT_PATH, audio=False)


if __name__ == '__main__':
    detect_on_images()
    # detect_on_video()
