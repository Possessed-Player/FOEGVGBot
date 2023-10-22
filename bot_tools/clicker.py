from .utils        import sleep
from random        import randrange
from pynput.mouse  import Controller
from pynput.mouse  import Button     as msbtn
from .utils        import to_point, reposition
from .visualobject import Vobj
from .imageobject  import ImgObj
#-----------------------------------------------------------------------
# Data Definitions:
#
# Clickable is one of:
# - Point
# - Vobj
# 
# Interp. Represents anything that has coordinates on screen 
#
#----------------------------------------------------------------------
class Clicker:
    def __init__(self):
        self._mouse = Controller()

    # Clickable, *String, *float, *float, *int, *float -> None
    # Given a point representing coordinates on screen click on it
    #   using either the left or right mouse button
    #       hold  -> how long to hold the mouse button before releasing
    #       hover -> how long to wait after moving the mouse before clicking
    #       times -> click how many times
    #       delay -> when clicking many times how long to wait between clicks
    def click(self, ca=None, btn="left", hold=0.25, hover=0, times=1, delay=0):
        p = self._ca_rrc(ca)
        
        btn = eval("msbtn." + btn)
        self.move(p)
        sleep(hover)

        for i in range(times):
            self.press(btn)
            sleep(hold)
            self.release(btn)
            sleep(delay)
     
    # Point, Point, String, *int -> None
    # Press and hold the given mouse button from point pa
    # to point pb then release
    def drag(self, pa, pb, btn, hover=0.25):
        self.move(pa)
        sleep(hover)
        self.press(btn)
        self.move(pb)
        self.release(btn)

    # Point -> None
    # Move mouse cursor to the coordinates represented by the given point
    def move(self, p):
        self._mouse.position = p

    # pynput.mouse.Key -> None
    # Press and hold the given mouse button
    def press(self, btn):
        self._mouse.press(btn)

    # pynput.mouse.Key -> None
    # Release the given mouse button
    # (should be used after calling press to release the mouse button)
    def release(self, btn):
        self._mouse.release(btn)

    # None -> Point
    # Return the current cursor position on screen
    def position(self):
        return self._mouse.position

    # Clickable -> Point
    # Randomize, Reposition and Correct given Clickable
    # return Point representing that clickable position on screen
    def _ca_rrc(self, ca):
        match ca:
            case None:
                return self._mouse.position
            case ImgObj(x=x, y=y, width=w, height=h):
                addx, addy = randrange(5, w - 5), randrange(5, h - 5)
                
                return reposition((x, y), (addx, addy))
            case Vobj(x=x, y=y, width=w, height=h) | ((x, y), (w, h)):
                addx, addy = randrange(w) if w != 0 else 0, randrange(h) if h != 0 else 0
            
                return reposition((x, y), (addx, addy))
            case _:
                return ca