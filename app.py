import os
import requests
from urllib.parse import urlparse
from io import BytesIO
from PIL import Image, ImageDraw
from azure.cognitiveservices.vision.face import FaceClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.face.models import TrainingStatusType, Person
from flask import Flask, request, render_template

# This key can be found in Keys and Endpoint in your Face resource.
KEY = "YOUR_SUBSCRIPTION_KEY"

# This enpoint can be found in Keys and Endpoint in your Face resource.
ENDPOINT = "YOUR_API_ENDPOINT"

face_client = FaceClient(ENDPOINT, CognitiveServicesCredentials(KEY))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def my_form_post():
    # Capture image URL
    single_face_image_url = request.form['text']
    single_image_name = os.path.basename(single_face_image_url)
    
    # For this example I will use detection_02.  
    # https://docs.microsoft.com/en-us/azure/cognitive-services/face/face-api-how-to-topics/specify-detection-model
    detected_faces = face_client.face.detect_with_url(url=single_face_image_url, detection_model='detection_02')
    
    # Exception if no image found
    if not detected_faces:
        raise Exception('No face detected from image {}'.format(single_image_name))

    # Convert the height and width to a point in a rectangle
    def getRectangle(faceDictionary):
        rect = faceDictionary.face_rectangle
        left = rect.left
        top = rect.top
        right = left + rect.width
        bottom = top + rect.height
        
        return ((left, top), (right, bottom))

    # Download the image from the url
    response = requests.get(single_face_image_url)
    img = Image.open(BytesIO(response.content))

    # For each face returned use the face rectangle and draw a red box.
    # https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html
    print('Drawing rectangle around face... see popup for results.')
    draw = ImageDraw.Draw(img)
    for face in detected_faces:
        draw.rectangle(getRectangle(face), outline='red', width=4)

    # Display the image in the users default image browser.
    img.show()

    # Return user to index.html
    return render_template('index.html')