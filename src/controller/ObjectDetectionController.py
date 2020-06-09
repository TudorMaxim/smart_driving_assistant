import cv2
import torch
from random import randint
from torch.autograd import Variable
from model.Darknet import Darknet
from utils.Constants import Constants
from utils.ImageUtils import ImageUtils
from utils.DetectionUtils import DetectionUtils


class ObjectDetectionController:
    def __init__(self, confidence_threshold=0.8, nms_threshold=0.4, image_size=416, tiny=False):
        self.model_cfg = Constants.ROOT_PATH + 'config/yolov3.cfg'
        self.weights_path = Constants.ROOT_PATH + 'config/yolov3.weights'
        if tiny:
            self.model_cfg = Constants.ROOT_PATH + 'config/yolov3-tiny.cfg'
            self.weights_path = Constants.ROOT_PATH + 'config/yolov3-tiny.weights'
        self.class_path = Constants.ROOT_PATH + 'config/coco.names'
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.image_size = image_size
        self.font_scale = 1
        self.font = cv2.FONT_HERSHEY_PLAIN
        self.classes = DetectionUtils.load_classes(self.class_path)
        # self.colors = [(randint(0, 255), randint(0, 255), randint(0, 255)) for _ in range(len(self.classes))]
        self.colors = [(0, 205 , 0) for _ in range(len(self.classes))]
        self.model = self.__load_model()

    def __load_model(self):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = Darknet(self.model_cfg, img_size=self.image_size).to(device)
        model.load_darknet_weights(self.weights_path)
        model.eval()
        return model

    def draw_bounding_boxes(self, image, detections):
        if detections is None:
            return image
        if len(detections) == 0:
            return image
        detections = DetectionUtils.rescale_boxes(detections, self.image_size, image.shape[:2])
        for x1, y1, x2, y2, conf, cls_conf, cls_pred in detections:
            color = self.colors[int(cls_pred)]
            text = self.classes[int(cls_pred)] + ' ' + str(int(cls_conf * 100)) + '%'
            width, height = cv2.getTextSize(text, self.font, self.font_scale, thickness=1)[0]
            image = cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            image = cv2.rectangle(image, (x1, y1), (x1 + width + 5, y1 - height - 10), color, cv2.FILLED)
            image = cv2.putText(image, text, (x1, y1 - height / 2), self.font, self.font_scale, (255, 255, 255), 1)
        return image

    def detect(self, image):
        Tensor = torch.cuda.FloatTensor if torch.cuda.is_available() else torch.FloatTensor
        image_tensor = ImageUtils.get_image_tensor(image, self.image_size).unsqueeze(0)
        image_tensor = Variable(image_tensor.type(Tensor))
        self.model.eval()
        with torch.no_grad():
            detections = self.model(image_tensor)
            detections = DetectionUtils.non_max_suppression(
                detections,
                self.confidence_threshold,
                self.nms_threshold
            )
            detections = detections[0]  # only for 1 image
        return detections
