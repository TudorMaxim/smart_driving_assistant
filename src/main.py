from controller.DrivingAssistantController import DrivingAssistantController


if __name__ == '__main__':
    controller = DrivingAssistantController(
        root_path='../'
    )
    # controller.detect_on_images()
    controller.detect_on_video()
