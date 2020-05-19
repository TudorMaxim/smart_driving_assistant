import io

import cv2
import numpy as np
from flask import Flask, request, jsonify, send_file
from controller.DrivingAssistantController import DrivingAssistantController

app = Flask(__name__)
controller = DrivingAssistantController(root_path='./src/')


@app.route("/")
def home():
    return "Hello, World!"


@app.route("/api/process/image", methods=['POST'])
def process_image():
    file = request.files['image'].read()
    np_image = np.fromstring(file, np.uint8)
    image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)
    controller.reset_lanes()
    result = controller.detect(image)
    return send_file(
        io.BytesIO(result),
        mimetype='image/jpeg',
        as_attachment=True,
        attachment_filename='result.jpg'
    )


if __name__ == "__main__":
    app.run(debug=True)
