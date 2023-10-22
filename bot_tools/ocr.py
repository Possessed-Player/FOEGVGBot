from .visualobject import Vobj
import cv2 as cv
from pytesseract import image_to_string


class NumReader(Vobj):
    def __init__(self, sz, dst):
        super().__init__()
        self.size = sz
        self.locations = [dst]
        
    # None -> bool
    # Override Vobj find method(to avoid exception)
    def find(self):
        return True
        
    # None -> int|None
    # Detect the number in area specified by the current object
    #   return None if wan't able to detect the number
    def read(self):
        img = self.cm.capture()
        
        x1, y1 = self.locations[0][0], self.locations[0][1]
        x2, y2 = x1 + self.width, y1 + self.height
        
        img = img[y1:y2, x1:x2, :]
        
        img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        
        img = cv.threshold(img, 125, 255, cv.THRESH_BINARY)[1]
        
            
        opts = "--psm 7 -c tessedit_char_whitelist=0123456789"
        
        res = image_to_string(img, config=opts)
        
        if res == "":
            return None
        else:
            return int(res)
            