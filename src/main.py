from controller.DrivingAssistantController import DrivingAssistantController


if __name__ == '__main__':
    controller = DrivingAssistantController(plot=True)
    controller.detect_on_images()
    # controller.detect_on_video()
