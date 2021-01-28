from flask import Flask, request, jsonify, render_template
from PIL import Image
import numpy as np
import base64
import io
import os
import numpy as np
import cv2

confidenceThreshold = 0.5
NMSThreshold = 0.3
modelConfiguration = r"C:\Users\krish\PycharmProjects\Object\Model\yolov3.cfg"
modelWeights = r"C:\Users\krish\PycharmProjects\Object\Model\yolov3.weights"
labelsPath = r'C:\Users\krish\PycharmProjects\Object\Model\coco.names'
labels = open(labelsPath).read().strip().split('\n')
np.random.seed(10)
COLORS = np.random.randint(0, 255, size=(len(labels), 3), dtype="uint8")
net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
app = Flask(__name__, static_url_path="/static", template_folder='template')

@app.route('/')
def main():
    return render_template('index.html')


@app.route('/api/', methods=["POST"])
def main_interface():
    response = request.get_json()
    data_str = response['image']
    point = data_str.find(',')
    base64_str = data_str[point:]  # remove unused part like this: "data:image/jpeg;base64,"
    image = base64.b64decode(base64_str)
    img = Image.open(io.BytesIO(image))
    if (img.mode != 'RGB'):
        img = img.convert("RGB")
    image = np.array(img)
    (H, W) = image.shape[:2]
    layerName = net.getLayerNames()
    layerName = [layerName[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layersOutputs = net.forward(layerName)
    boxes = []
    confidences = []
    classIDs = []
    for output in layersOutputs:
        for detection in output:
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]
            if confidence > confidenceThreshold:
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype('int')
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)

    detectionNMS = cv2.dnn.NMSBoxes(boxes, confidences, confidenceThreshold, NMSThreshold)
    coordinates = []
    if (len(detectionNMS) > 0):
        for i in detectionNMS.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])
            color = [int(c) for c in COLORS[classIDs[i]]]
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
            text = '{}: {:.4f}'.format(labels[classIDs[i]], confidences[i])
            cv2.putText(image, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            img = Image.fromarray(image)
            rawBytes = io.BytesIO()
            img.save(rawBytes, "JPEG")
            rawBytes.seek(0)
            img_base64 = base64.b64encode(rawBytes.read())
            coordinates.append({"Top-left": [x, y], "Bottom-right": [x + w, y + h]})
    response = jsonify({"image": str(img_base64), "coordinates": coordinates})
    return response



@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
