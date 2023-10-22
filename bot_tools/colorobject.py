import cv2 as cv
import numpy as np
from math          import dist, sqrt
from .visualobject import Vobj
from time          import sleep


class ColorObj(Vobj):
    # tuple(Color, Color), int, int -> ColorObj
    def __init__(self, lwr, upr, min=None, max=None, one=False):
        super().__init__()
        self.lower, self.upper = (np.array(lwr), np.array(upr))
        self.minimum = min
        self.maximum = max
        self.one     = one
        self.size    = ((round(sqrt(min)), round(sqrt(min))) if not (min is None) else (0, 0)
                        if not self.one else (0, 0))
        if not self.one:
            self.sizes   = {}
    
    # None -> bool
    # Find current color object in cm.capture()(Should yield an Image)
    # Return True  if found
    #        False if not found
    def find(self):
        img = self.cm.capture()
        while img is None:
            img = self.cm.capture()
            sleep(0.25)
        
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        
        result = cv.inRange(hsv, self.lower, self.upper)
        result = cv.dilate(result, None, iterations=2)
        cnts = cv.findContours(result.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        
        found = False if not self.one else len(cnts[0]) > 0
        
        if self.one:
            bgst = None
            bgst_a = 0
        else:
            locations = []
            
        for c in cnts[0]:
            (x, y, w, h) = cv.boundingRect(c)
            area = w * h

            if self.one:
                if area > bgst_a:
                    bgst   = (x, y, w, h)
                    bgst_a = area
            else:
                if (((not (self.minimum is None)) and area < self.minimum) or 
                    ((not (self.maximum is None)) and area > self.maximum)):
                        continue
                else:
                    locations.append((x, y))
                    self.sizes[(x, y)] = (w, h)
                    found = True
                
        if self.one:
            if found:
                self.locations = [[bgst[0], bgst[1]]]
                self.size      = bgst[2], bgst[3]
        else:
            self.locations = locations

        return found
        
        
class DcolorObj(Vobj):
    # ColorObj, ColorObj, int -> DcolorObj
    def __init__(self, coal, coau, cobl, cobu, mndst):
        super().__init__()
        self.cobja = coal, coau
        self.cobjb = cobl, cobu
        self.size  = (coa.size[0] if coa.size[0] > cob.size[0] else cob.size[0],
                      coa.size[1] if coa.size[1] > cob.size[1] else cob.size[1])
        self.min_dst = mndst
        
    # None -> bool
    # Find current double color object in cm.capture()
    def find(self):
        self.cobja.find()
        self.cobjb.find()
        
        found = False
        locations = []
        for coa in self.cobja.locations:
            for cob in self.cobjb.locations:
                if dist(coa, cob) <= self.min_dst:
                    locations.append((coa[0] + round(self.size[0] * 0.25), 
                                      coa[1] + round(self.size[1] * 0.25)))
                    found = True
                    
        self.locations = locations
        return found