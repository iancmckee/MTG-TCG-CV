
import cv2
import pytesseract
import difflib
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
import numpy as np
from easygui import *
import wmi
import re
import collections

# gets passed an error for no Sequence in collections
collections.Mapping = collections.abc.Mapping
collections.Sequence = collections.abc.Sequence

# directory of py tesseract, installed in accordance with the readme
# for windows you can use the following format as an example
pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

def selectCam():
    cameras = []
    c = wmi.WMI()
    wql = "Select * From Win32_USBControllerDevice"
    i = 0
    for item in reversed(c.query(wql)):
        p = item.Dependent.PNPClass
        if p is not None and re.findall("Camera", p):
            print(p)
            cameras.append(str(item.Dependent.Name))
            i = i + 1
    print(cameras)
    return cameras


def populateSet(url, setMap):
    uClient = uReq(url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    cards_table = page_soup.findAll('tbody')

    for cards in cards_table:
        cardRows = cards.findAll('tr')
        for card in cardRows[1:]:
            cardInfo = card.findAll('td')
            cardName = cardInfo[1].find_all('a', {})
            if len(cardName) >= 1:
                # name = cardInfo[1].text
                name = cardName[0].text
            badges = cardInfo[1].find_all('span', {'class', 'badge'})
            if len(badges) >= 1:
                for badge in badges:
                    # print("Badges: ", badge.text)
                    name = name + "(" + badge.text[0:1] + ")"
            price = cardInfo[4].text
            # print(name)
            # print("Price: ", price)
            setMap.add(name, price)

    return setMap.getList()


# Create your setMap class
class key_value_Map(dict):
    # __init__ function
    def __init__(self):
        self = dict()

    # Function to add key:value
    def add(self, key, value):
        self[key] = value

    def getList(dict):
        return dict.keys()


def populateSetList(setListMap):
    set_url = "https://www.mtggoldfish.com/sets/"
    uClient = uReq(set_url)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    result = page_soup.find_all('li', {'class', 'sets-set-information-name'})
    for set_name in result:
        if set_name.a:
            setListMap[set_name.text] = set_name.a.get('href')
    return setListMap


def back(*args):
    pass


# #-----------------------------------------------------------------------------------------------------------------------

# #The following Stuff Is Initalizing Adventures of the Forgotten Realms Trading Cards
# #-----------------------------------------------------------------------------------------------------------------------
# Pulling info from mtggoldfish
# set_name = "Innistrad+Midnight+Hunt"
# set_name = "Adventures+in+the+Forgotten+Realms"
# my_url = "https://www.mtggoldfish.com/sets/"+set_name+"#paper"

setMap = key_value_Map()
setListMap = key_value_Map()
setListMap = populateSetList(setListMap)
choices = setListMap.getList()

# creating a multi choice box
camsAvail = selectCam()
print(len(camsAvail))
if len(camsAvail) > 1:
    camChoice = choicebox("Selected which Camera will be viewing the cards", "Cameras in Device Manager", camsAvail)
else:
    camChoice = camsAvail[0]
setChoice = choicebox("Selected any set from the list given below", "Magic the Gathering Sets", choices)
set_name = setListMap[setChoice]
my_url = "https://www.mtggoldfish.com" + set_name + "/Main+Set#paper"
cardBank = populateSet(my_url, setMap)

frameWidth = 1280
frameHeight = 960
cap = cv2.VideoCapture(camsAvail.index(camChoice))
# cap = cv2.VideoCapture(1)
cap.set(3, frameWidth)
cap.set(4, frameHeight)


def newSet(setMap):
    setChoice = choicebox("Selected any set from the list given below", "Magic the Gathering Sets", choices)
    set_name = setListMap[setChoice]
    # print("Set Chosen: ", setChoice, " With Url: ", set_name)
    my_url = "https://www.mtggoldfish.com" + set_name + "#paper"
    cardBank = populateSet(my_url, setMap)

def empty(a):
    pass

cv2.namedWindow("Parameters")
cv2.resizeWindow("Parameters", 640, 180)
cv2.createTrackbar("Threshold1", "Parameters", 100, 255, empty)
cv2.createTrackbar("Threshold2", "Parameters", 140, 255, empty)
cv2.createTrackbar("Area", "Parameters", 35000, 100000, empty)

if not cap.isOpened():
    raise IOError("Cannot open webcam")


def stackImages(scale, imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range(0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape[:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]),
                                                None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y] = cv2.cvtColor(imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank] * rows
        hor_con = [imageBlank] * rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None, scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor = np.hstack(imgArray)
        ver = hor
    return ver


def getContours(img, imgContour, originalImg, imgConts, setMap):
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    width, height = 500, 700
    price = ""

    for cnt in contours:
        area = cv2.contourArea(cnt)
        areaMin = cv2.getTrackbarPos("Area", "Parameters")
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        # if area > areaMin and len(approx) == 4:
        if area > areaMin and len(approx) == 4:
            # print("Area: ",area)
            cv2.drawContours(imgConts, cnt, -1, (255, 0, 255), 7)
            rectX, rectY, rectW, rectH = cv2.boundingRect(approx)
            cv2.rectangle(imgContour, (rectX, rectY), (rectX + rectW, rectY + rectH), (0, 255, 0), 5)
            # cv2.putText(imgContour, "Points: " + str(len(approx)), (x+20, y+20), cv2.FONT_HERSHEY_COMPLEX, .7, (0,255,0), 2)
            points = []
            # i = 0
            for point in approx:
                x, y = point[0]
                points.append([x, y])
            card = np.float32(points)
            x1, y1 = points[0]
            x2, y2 = points[1]
            x3, y3 = points[2]
            x4, y4 = points[3]

            # distance formula
            # sqrt( (x2-x1)^2 + (y2-y1)^2 )
            # This should make it so if it's cocked it still gets put into up, down regardless if it's cocked
            # left or cocked right
            if np.sqrt(np.square(x1 - x2) + np.square(y1 - y2)) < np.sqrt(np.square(x1 - x4) + np.square(y1 - y4)):
                # top point goes to top right
                cardWarped = np.float32([[width, 0], [0, 0], [0, height], [width, height]])
            else:
                # top point goes to top left
                cardWarped = np.float32([[0, 0], [0, height], [width, height], [width, 0]])
            matrix = cv2.getPerspectiveTransform(card, cardWarped)
            imgOutput = cv2.warpPerspective(originalImg, matrix, (width, height))
            card_name, price = getPrice(setMap, imgOutput, width, height)
            if card_name == "Not Found in Chosen Set":
                textColor = (0, 0, 255)
            else:
                textColor = (255, 50, 0)
            cv2.putText(imgContour, (card_name + " " + price), (rectX, rectY - 20), cv2.FONT_HERSHEY_COMPLEX, .7,
                        textColor, 2)


def getPrice(setMap, img, width, height):
    card_title = img[25:75, 34:400]
    # cv2.imshow("Card Name",card_title)

    card_name = re.sub('[^a-zA-Z0-9,+ ]', '', pytesseract.image_to_string(card_title))

    # print("Card name: ", card_name)

    closest_match = difflib.get_close_matches(card_name, cardBank)
    if len(closest_match) >= 1:
        # print("Closest Matches",closest_match)
        closest_match = closest_match[0]
        price = re.sub('[^0-9$.]', '', setMap[closest_match])
    else:
        closest_match = "Not Found in Chosen Set"
        price = ""

    return closest_match, price


# Future Improvement multiple cards

while True:
    success, img = cap.read()
    imgContour = img.copy()
    imgConts = img.copy()

    imgBlur = cv2.GaussianBlur(img, (5, 5), 0)
    imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)

    threshold1 = cv2.getTrackbarPos("Threshold1", "Parameters")
    threshold2 = cv2.getTrackbarPos("Threshold2", "Parameters")
    imgCanny = cv2.Canny(imgGray, threshold1, threshold2)
    kernel = np.ones((5, 5), np.uint8)
    imgDil = cv2.dilate(imgCanny, kernel, iterations=1)

    getContours(imgDil, imgContour, img, imgConts, setMap)

    imgStack = stackImages(0.8, ([img, imgGray, imgCanny],
                                 [imgConts, imgContour, img]))
    cv2.imshow("MTG Price Lookup OpenCV Project", imgContour)
    # If you'd like to see how the sliders are changing how the system views the card, uncomment line 275
    # cv2.imshow('Full Explanation', imgStack)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
