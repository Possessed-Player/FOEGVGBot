from time   import time, sleep as _sleep
from random import uniform
from math   import dist
#---------------------------------------------------------------------
# Data Definitions:
#
# Relative is one of:
# - ""
# - "mid"
# - "bot"
# - "lbot"
# - "rbot"
# - "top"
# - "rtop"
#
# Interp. is a relativity coordinated tag for visual objects
#    rel = ""     -> (default) return a Point referencing to the top left corner
#    rel = "mid"  -> center point of visual object
#    rel = "bot"  -> bottom of visual object midway
#    rel = "lbot" -> left bottom corner of visual object
#    rel = "rbot" -> right bottom corner of visual object
#    rel = "top"  -> top of visual object midway
#    rel = "rtop" -> right top corner of visual object
#
#---------------------------------------------------------------------
# Vobj, Relative -> Point
# Given a Vobj return coordinates of relative to it's location
def to_point(vo, rel="mid"):
    match rel:
        case "":
            p = (vo.x, vo.y)
        case "mid":
            p = (vo.x  + (vo.width // 2) , vo.y + (vo.height // 2))
        case "bot":
            p = (vo.x  + (vo.width // 2) , vo.y + vo.height)
        case "lbot":
            p = (vo.x                    , vo.y + vo.height)
        case "rbot":
            p = (vo.x + vo.width         , vo.y + vo.height)
        case "top":
            p = (vo.x + (vo.width // 2)  , vo.y)
        case "rtop":
            p = (vo.x + vo.width         , vo.y)
        case _:
            raise "Relative function given wrong rel value"
    
    return p

# Point, Point -> Point
# Reposition point a by adding point b to it and return the result
def reposition(pa, pb):
    return (pa[0] + pb[0], pa[1] + pb[1])


# Vobj, click function, Relative, Point -> function
# Produces a function when called finds the Vobj then clicks on it
#   Relative -> modify vo to a point relative to the visual object
#   Point    -> reposition the modified point by adding rps to it
#   *args    -> Arguements streamed to the click function
def routine(vo, cf, rel="mid", rps=(0, 0), *args):
    def helper():
        vo.find()
        p = to_point(vo, rel)
        p = reposition(p, rps)
        cf.click(p, **args)

    return helper

# Vobj, String, Point -> None
# Sort visual object locations based on given String keys
# String : selects the method to sort with
def sort(vo, k, p=(0, 0)):
    match k:
        case "CLOSEST_TO_MID":
            p  = vo.cm.midpoint
            srt_f = lambda loc: dist(p, loc)
        case "SMALLEST_X":
            srt_f = lambda loc: loc[0]
        case "SMALLEST_Y":
            srt_f = lambda loc: loc[1]
            
    vo.locations = sorted(vo.locations, key=srt_f)
    
        
        
# float -> None
# Sleep for the given time as float
def sleep(f):
    if f < 0.25:
        t = time()
        while (t + f) > time():
            pass
    else:
        _sleep(f)
        
        
# Vobj, float -> bool
# Run an infinite loop until the Vobj find function returns True
# when max_t is larger than 0 this function stop when max_t seconds elapsed instead
# of running indefinitely
# return True  -> found the Vobj
# return False -> Vobj not found(only when max_t is > 0)
def wait_for(vo, max_t=0):
    if max_t > 0:
        st = time()
        while not vo.find():
            if (st + max_t <= time.time()):
                return False
                
            sleep(0.1)
    else:    
        while not vo.find():
            sleep(0.1)
    
    return True
    
# float, float -> None
# Sleep within a random range of a fraction of given seconds
# float -> sleep interval in seconds
# float -> ratio of sleep interval to add/substract from original sleep interval
def rndsleep(f, fr=0.10):
    ad = f * fr
    lw, up = f - ad, f + ad
    sleep(uniform(lw, up))