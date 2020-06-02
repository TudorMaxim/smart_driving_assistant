import glob
import cv2
from moviepy.video.io.VideoFileClip import VideoFileClip
from controller.LaneDetectionController import LaneDetectionController

IN_VIDEO_PATH = '../input/videos/project_video.mp4'
OUT_VIDEO_PATH = '../results/videos/project_video_ld.mp4'
IN_IMAGES_PATH = '../input/images/test*.jpg'


def detect_on_images():
    paths = glob.glob(IN_IMAGES_PATH)
    images = [cv2.imread(path) for path in paths]
    lane_detection_controller = LaneDetectionController(plot=True)
    for image, path in zip(images, paths):
        print("Image " + path)
        result = lane_detection_controller.process_image(image)
        image_name = path.split("\\")[-1]
        cv2.imshow(image_name, result)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


def detect_on_video():
    lane_detection_controller = LaneDetectionController()
    video = VideoFileClip(IN_VIDEO_PATH)
    output_video = video.fl_image(lane_detection_controller.process_video)
    output_video.write_videofile(OUT_VIDEO_PATH, audio=False)


if __name__ == '__main__':
    detect_on_images()
    # detect_on_video()
