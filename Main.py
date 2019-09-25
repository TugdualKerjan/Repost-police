import requests
from PIL import Image
import pprint as pp
import base64
import Analyzer

# Get the initial memes
response = requests.get("http://9gag.com")
jsonResponse = response.text
position = jsonResponse.find('"position":1,"url":"https:\\/\\/9gag.com\\/gag\\/')
position = position + len('"position":1,"url":"https:\\/\\/9gag.com\\/gag\\/')
nextCursor = jsonResponse[position:position + 7]
initUrl = "https://9gag.com/v1/group-posts/group/default/type/hot?%s" % nextCursor
response = requests.get(initUrl)
jsonResponse = response.json()
amountOfMemes = int(len(jsonResponse['data']['posts'])) - 1
nextCursor = jsonResponse['data']['nextCursor']

information = ""
index = 0

def getNextImage(string: str):
    print(string)
    image = requests.get("https://img-9gag-fun.9cache.com/photo/%s_460s.jpg" % string)
    set_labels(string, image)

def set_labels(id:str, image:Image):
    global information, index
    encoded_string = base64.b64encode(image.content)
    string = str(encoded_string)[2:].replace("=", "").replace("'", "")
    data = {
        "requests": [
            {
                "features": [
                    {
                        "type": "WEB_DETECTION"
                    }
                ],
                "image": {
                    "content": string
                }
            }
        ]
    }
    url = 'https://vision.googleapis.com/v1/images:annotate?key=AIzaSyAaUWCxudFLzdOXXrr5BA9wN-tdr02f8c4'
    description = requests.post(url, json=data)
    pp.pprint(description.json())
    lines = []
    try:
        lines = description.json()['responses'][0]['webDetection']['pagesWithMatchingImages']
    except:
        pass

    matched_links = ""
    for item in lines:
        try:
            matched_links += str(item['fullMatchingImages'][0]['url']) + ", "
        except:
            pass

    information += str(index) + ": " + id + ": " + matched_links + "\n"
    index += 1



def checkIfLast():
    global amountOfMemes, nextCursor, initUrl, response, jsonResponse
    if amountOfMemes == 0:
        initUrl = "https://9gag.com/v1/group-posts/group/default/type/hot?%s" % nextCursor
        response = requests.get(initUrl)
        jsonResponse = response.json()
        amountOfMemes = int(len(jsonResponse['data']['posts'])) - 1
        nextCursor = jsonResponse['data']['nextCursor']

def callback():
    global amountOfMemes
    if jsonResponse['data']['posts'][amountOfMemes]['type'] != "Photo":
        amountOfMemes = amountOfMemes - 1
        checkIfLast()
        return callback()
    elif int(jsonResponse['data']['posts'][amountOfMemes]['upVoteCount']) <= 1000:
        amountOfMemes = amountOfMemes - 1
        checkIfLast()
        return callback()
    else:
        identifier = jsonResponse['data']['posts'][amountOfMemes]['id']
        amountOfMemes = amountOfMemes - 1
        getNextImage(identifier)
        checkIfLast()

for i in range (0, 100):
    for n in range(0, 100):
        callback()
    file = open('log.txt', 'a')
    file.write(information)
    file.close()
    information = ""

