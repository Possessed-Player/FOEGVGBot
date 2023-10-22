from .visualobject import Vobj
import cv2 as cv
import numpy as np
from math import dist
from time import sleep
#---------------------------------------------
# Data Definitions:
#
# Point is each of:
# - x : int
# - y : int
#
# interp. Is a point in a 2D plane.
#
#
#--------------------------------------------
class ImgObj(Vobj):
    THRESH = 0.8
    METHOD = "cv.TM_CCOEFF_NORMED"

    def __init__(self, p):
        super().__init__()
        self.image   = cv.imread(p)
        self.size    = self.image.shape[::-1][1:]
        self.thresh  = ImgObj.THRESH
        self.method  = ImgObj.METHOD

    # None -> bool 
    # Find the best matching clone of the  current ImgObj in cman.capture() 
    # and Update its locations,
    # Return True  if at least one object was found
    #        False if no object was found
    def find(self):
        result = self._template_match()
        
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        
        if "SQDIFF" in self.method:
            self.locations = [min_loc]
            
            return min_val < self.thresh
        else:
            self.locations = [max_loc]
                
            return max_val > self.thresh

    # None -> bool 
    # Find all clones of the current ImgObj in cman.capture() 
    # and Update its locations,
    # Return True  if at least one object was found
    #        False if no object was found
    def find_all(self):
        result = self._template_match()

        if "SQDIFF" in self.method:
            loc = np.where(result < self.thresh)
        else:
            loc = np.where(result > self.thresh)

        self.locations = [pt for pt in zip(*loc[::-1])]

        return loc[0].size > 0


    # None -> List of (float, Point)
    # Find self image in cman.capture() and return all the results
    def _template_match(self):
        parent = self.cm.capture()
        while parent is None:
            parent = self.cm.capture()
            sleep(0.25)
        
        gparent = cv.cvtColor(parent, cv.COLOR_BGR2GRAY)
        gself   = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)

        return cv.matchTemplate(gparent, gself, eval(self.method))

                



            
# ImgObj is Vobj extended to include:
# - image   : String
# - cm      : CameraMan
# - thresh  : float
# - method  : String
# 
# Interp. This is a visualobject class specialized in image
#           based object detection
#           image   -> Image file path as string.
#           cm      -> CameraMan object handles screen related activities
#           thresh  -> Least acceptable template matching score.
#           method  -> Method to use in template matching.
#           
#
#
# This class should include methods to find the images specified
# on another image or on screen.
