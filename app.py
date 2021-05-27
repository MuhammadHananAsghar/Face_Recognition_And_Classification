from flask import Flask, render_template, request, redirect, url_for, jsonify
import matplotlib.pyplot as plt
from mtcnn import MTCNN
import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras.models import model_from_json
import base64
import uuid
import cv2

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=['POST'])
def predict():
    pic_data = request.form['URI']
    unique_filename = str(uuid.uuid4())
    pic_data = pic_data.replace("data:image/jpeg;base64,", "")
    imgdata = base64.b64decode(pic_data)
    filename = f'{unique_filename}.jpg'
    with open(filename, 'wb') as f:
        f.write(imgdata)
    predicted, percentage = get_prediction(filename)
    output = f"This model predicted this image as {predicted} with the accuracy of {str(percentage)}%."
    return jsonify(objt=output)


def get_prediction(image):
    detector = MTCNN()
    class_names = ['Bill Gates', 'Elon Musk',
                   'Jeff Bezos', 'Mark Zuckerberg', 'Steve Jobs']
    imge = plt.imread(image)
    boxes = detector.detect_faces(imge)
    boxes = boxes[0]['box']
    boxes = [int(i) for i in boxes]
    x1, y1, width, height = boxes
    x2, y2 = x1 + width, y1 + height
    face_image = imge[y1:y2, x1:x2]
    face_image = cv2.resize(face_image, (70, 70))

    img_array = keras.preprocessing.image.img_to_array(face_image)
    img_array = tf.expand_dims(img_array, 0)
    json_file = open('model.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)
    loaded_model.load_weights("model.h5")
    predictions = loaded_model.predict(img_array)
    score = tf.nn.softmax(predictions[0])
    predicted = class_names[np.argmax(score)]
    percentage = round(100 * np.max(score), 2)
    return predicted, percentage


if __name__ == "__main__":
    app.run(debug=True)
