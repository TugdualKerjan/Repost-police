from PIL import Image
import pprint as pp
from io import BytesIO
import requests
from PIL.ExifTags import TAGS

import warnings
warnings.filterwarnings("ignore")

def imageData(url:str):
    response = requests.request('get', url)
    image = Image.open(BytesIO(response.content))
    print('called')
    print(image._getexif().items().__len__)
    for (k, v) in image._getexif().items():
        print(str(TAGS.get(k)) + " = " + v)
