import json

from tabjudge.Point import Point
import cv2
import json
import base64

class TabletData:
    
    #RectPoint = RectanglePoint(10,20,50, 100)
    #ResponseData(RectanglePoint(10,20,50, 100), listData , "/image.png" )
    
    def __init__(self, pointList, candiList, imagePath):
        #Android側と名称一致させること
        self.data = "aaaaa"
        self.pointList = pointList
        self.candidateList = candiList
        print(imagePath)
        image = cv2.imread(imagePath)
        _, encimg = cv2.imencode(".png", image)
        img_str = encimg.tostring()
        #self.ImageData = base64.b64encode(img_str).decode("utf-8")
        self.trimBmpData = base64.b64encode(img_str).decode("utf-8")
