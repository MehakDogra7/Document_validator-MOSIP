import requests
import pytesseract
import cv2
import os
import numpy as np
import matplotlib.pyplot as plt
from pytesseract import Output
from PIL import Image
import json

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/document-validator", methods=['POST'])
def hello():
    try:
        imageFile = request.files['uploaded']
        type = request.form['type']
        formData = request.form['demographicData']
        imageFile.save(imageFile.filename)

        #print(imageFile)
        #print("Code succcesful")

        if(os.path.getsize(imageFile.filename)>12000000):
            return jsonify(error="Image size too large",code="413")

        image = cv2.imread(imageFile.filename)
        templatePath = './'+type+'.json'


        custom_config = r'--oem 3 --psm 6'

        with open(templatePath) as f:
            x = json.load(f)
        dimensions = image.shape
        dimensions_y = dimensions[0]
        dimensions_x = dimensions[1]
        x_percent = dimensions_x / 929
        y_percent = dimensions_y / 628

        if x_percent > 0.301 and y_percent > 0.300:
            print()
        else:
            return jsonify(error="Image size is not valid", code="422")

        y = json.loads(formData)
        length = len(y)
        attr = ""
        valid = 0

        for property in y:
            flag = 0
            for property1 in x:
                if(property1 == property):
                    y1 = int(x[property1]['y1'] * dimensions_y / 100)
                    y2 = int(x[property1]['y2'] * dimensions_y / 100)
                    x1 = int(x[property1]['x1'] * dimensions_x / 100)
                    x2 = int(x[property1]['x2'] * dimensions_x / 100)
                    property_cut = image[y1:y2, x1:x2]
                    propertyEvaluated = pytesseract.image_to_string(property_cut, config=custom_config, lang='hin+eng')
                    propertyOriginal = y[property]
                    if (propertyEvaluated.split() == propertyOriginal.split()):
                        valid = valid + 1
                    flag=1
                else:
                    continue
            if(flag != 1):
                attr = property + "/" + attr


        percentageOfAccuracy = (valid * 100 / length)

        if(flag != 1):
                return jsonify(error=attr + " attributes does not exists",accuracy=percentageOfAccuracy,code="420")
        else:
                return jsonify(accuracy=percentageOfAccuracy)

    except:
        return jsonify(error="Exception occured",code="500")

if __name__ == '__main__':
    app.run(debug=True)