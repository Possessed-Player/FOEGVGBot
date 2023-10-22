from win32gui import FindWindowEx, GetWindowRect
from .visualobject import Vobj
from threading import Lock, main_thread, Thread
import mss
import os
import numpy as np
from time import sleep


class CameraMan(Vobj):
    # String|None -> None
    # Initialize a CameraMan object, string is the name of the window
    #   if dealing with a window otherwise None to deal with the whole screen
    #   NOTE: WINDOW BASED CAMERA MAN ONLY WORKS ON WINDOWS OS!
    def __init__(self, name=None):
        super().__init__()
        self.name = name
        if self.name:
            self.iswin = True
            self.midpoint = (0, 0)
            self._update_winfo(name)
        else:
            self.iswin = False
            
        
        #self.lock = Lock()
        self._latest_img = None
        Thread(target=self._screenshot_generator).start()
        self.capture = lambda : (self._latest_img.copy() 
                                if not (self._latest_img is None) else None)
        
        
    # None, int[1..] -> Generator(Image as Numpy Array)
    # Returns a generator that yields images when called
    #   use second arguement to select the target monitor number
    def _screenshot_generator(self, mon=1):
        with mss.mss() as sct:
            if self.iswin:
                monitor = {"left" :self.x, "top"   :self.y,
                           "width":self.width, "height":self.height}
            else:
                monitor = sct.monitors[mon]
                
            while main_thread().is_alive():
                self._latest_img = np.array(sct.grab(monitor))
                #sleep(0.25)
            
            
    # None -> Image
    # Add a thread lock to getting the lastest image
    def _thread_safe(self):
        with self.lock:
            return self._latest_img.get().copy() if not self._latest_img.empty() else None
            
    # String -> int, int, int, int, int
    # Return the current coordinates of a window
    def __get_winfo(n):
        whnd = FindWindowEx(None, None, None, n)
        
        if whnd != 0:
            rect = GetWindowRect(whnd)
            return (whnd, rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])
        else:
            return (whnd, 0, 0, 0, 0)
        
    # String -> None
    # Check if the main window is open, raise an error if it's not on screen
    #  else update the main window x, y, width and height according
    #  to it's current details
    def _update_winfo(self, n):
       win = CameraMan.__get_winfo(n)
       
       if win[0] == 0:
           raise Exception("Couldn't find the specified window," +
                           " make sure the name is right and the window is open")
       else:
           self.locations[0] = win[1], win[2]
           self.size = win[3], win[4]
           self.midpoint = self.x + (self.width // 2), self.y + (self.height // 2)
            
            
    # None -> None
    # Correct the current CameraMan window position
    def recalibrate(self):
        if self.iswin:
            self._update_winfo(self.name)
            gen = self._screenshot_generator()
            self.capture = lambda : self._thread_safe(lambda: next(gen))
            
    # None -> bool
    # Overriding Vobj find method
    def find(self):
        return True
        
    # Point -> Color
    # Produce the pixel color on the specified coordinates given
    def get_pixel(self, p):
        img = self.capture()
        
        return img[p[1]][p[0]]
