import requests
import pytesseract
import cv2
import numpy as np
import matplotlib.pyplot as plt
from pytesseract import Output
from PIL import Image

from flask import Flask,jsonify,request

app = Flask(__name__)

@app.route("/", methods=['POST'])
def hello():
    type = request.form['type']
    imagePath = request.form['imagePath']
    templatePath = request.form['templatePath']
    dataPath = request.form['dataPath']
    print("Code succcesful")
    image = cv2.imread(imagePath)
    # plt.imshow(image)

    import json
    custom_config = r'--oem 3 --psm 6'

    with open(templatePath) as f:
        x = json.load(f)
    dimensions = image.shape
    dimensions_y = dimensions[0]
    dimensions_x = dimensions[1]
    x_percent = dimensions_x / 929
    y_percent = dimensions_y / 628

    if x_percent > 0.301 and y_percent > 0.300:
        print("Continue")
    else:
        return jsonify(error="Image size is not valid", code="422")
    with open(dataPath) as d:
        y = json.load(d)
    length = len(y)

    valid = 0
    for property in x:
        y1 = int(x[property]['y1'] * dimensions_y / 100)
        y2 = int(x[property]['y2'] * dimensions_y / 100)
        x1 = int(x[property]['x1'] * dimensions_x / 100)
        x2 = int(x[property]['x2'] * dimensions_x / 100)
        property_cut = image[y1:y2, x1:x2]
        propertyEvaluated = pytesseract.image_to_string(property_cut, config=custom_config, lang='hin+eng')
        propertyOriginal = y[property]
        if (propertyEvaluated.split() == propertyOriginal.split()):
            valid = valid + 1


    percentageOfAccuracy = (valid * 100 / length)
    return jsonify(accuracy=percentageOfAccuracy)


if __name__ == '__main__':
    app.run(debug=True)