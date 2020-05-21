import glob
import time
import datetime
import cv2
from moviepy.video.io.VideoFileClip import VideoFileClip

from controller.ObjectDetectionController import ObjectDetectionController

IMAGES_IN_PATH = '../input/images/*'
IMAGES_OUT_PATH = '../output/images/'
IN_VIDEO_PATH = '../input/videos/project_video.mp4'
OUT_VIDEO_PATH = '../output/videos/project_video_od.mp4'
object_detection_controller = ObjectDetectionController(root_path='../')


def detect_on_images():
    paths = glob.glob(IMAGES_IN_PATH)
    images = [cv2.imread(path) for path in paths]
    for image, path in zip(images, paths):
        start_time = time.time()
        detections = object_detection_controller.detect(image)
        end_time = time.time()
        inference_time = datetime.timedelta(seconds=end_time - start_time)
        print("Image: " + path)
        print("Inference Time: ", inference_time)
        result = object_detection_controller.draw_bounding_boxes(image, detections)
        filename = path.split("\\")[-1]
        # cv2.imwrite(IMAGES_OUT_PATH + filename, result)
        cv2.imshow(filename, result)
    cv2.waitKey(0)


def process_video(image):
    detections = object_detection_controller.detect(image)
    return object_detection_controller.draw_bounding_boxes(image, detections)


def detect_on_video():
    video = VideoFileClip(IN_VIDEO_PATH)
    output_video = video.fl_image(process_video)
    output_video.write_videofile(OUT_VIDEO_PATH, audio=False)


if __name__ == '__main__':
    detect_on_images()
    # detect_on_video()
