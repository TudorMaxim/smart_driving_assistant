import glob
import cv2
from utils.Constants import Constants


class DatasetUtils:
    def __init__(self, detections_path=Constants.DETECTIONS_PATH):
        self.detections_path = detections_path

    def save_detections(self, in_paths, out_paths):
        file = open(self.detections_path, 'w')
        for in_path, out_path in zip(in_paths, out_paths):
            line = in_path + ',' + out_path + '\n'
            file.write(line)

    def get_images_from_directory(self, directory_path):
        if directory_path[-1] != '/':
            directory_path += '/'
        print('Loading images from directory: ' + directory_path)
        paths = glob.glob(directory_path + "*.jpg") + glob.glob(directory_path + "*.png")
        images = [cv2.imread(path) for path in paths]
        print('Loaded ' + str(len(images)) + " images.")
        paths = [path.replace('\\', '/').rstrip('\n') for path in paths]
        return paths, images

    def load_detections(self):
        file = open(self.detections_path, 'r')
        lines = file.readlines()
        in_paths = []
        out_paths = []
        for line in lines:
            in_path, out_path = line.rstrip('\n').split(',')
            in_paths.append(in_path)
            out_paths.append(out_path)
        return in_paths, out_paths
