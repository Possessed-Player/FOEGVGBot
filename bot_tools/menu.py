from .visualobject import Vobj
from .imageobject  import ImgObj 
#-------------------------------------------------
# Data Definitions:
#
# Landmark is a pair of:
# - Vobj
# - bool
#
# Interp. Used to represent a special fixed visual object
#           inside a larger object,
#           as the large object might change internally 
#           leading to detection difficulties.
#              Vobj         -> is the special fixed visual object
#              bool : True  -> Means if Vobj is visible the large object
#                               is also visible and vice versa.
#                   : False -> Means if Vobj is visible the large object
#                               is not visible and vice versa.
#
#-------------------------------------------------
class ConstVobj(Vobj):
    def __init__(self, p, sz):
        super().__init__()
        self.locations[0] = p
        self.size         = sz
        
    # None -> True
    # <RETURNS True INVARIABELY>
    # Defined to avoid calling super class find
    def find(self):
        return True
        
class TethVobj(Vobj):
    # int, Size, Vobj -> FixedVobj
    def __init__(self, parnt, dst, sz):
        super().__init__()
        self.distance = dst
        self.size     = sz
        self.parent   = parnt

    # None -> bool 
    # Update the current FixedVobj location based on
    # the current self.parent location
    def find(self):
        found =  self.parent.find()
        
        if found:
            self.locations = [(self.parent.x + self.distance[0],
                               self.parent.y + self.distance[1])]
        
        return found


class LargeVobj(Vobj):
    # Landmark, Point -> LargeVobj
    def __init__(self, lm, dst=(0, 0)):
        super().__init__()
        
        match lm:
            case tuple() | list():
                self.landmark = lm
            case _:
                self.landmark = (lm, True)
            
        self.distance = dst

    # None -> bool
    # Return True  if current LVO is visible
    #        False if current LVO is not visible
    def find(self):
        found = self.landmark[0].find()

        if found:
            self.locations = [(self.landmark[0].x + self.distance[0],
                               self.landmark[0].y + self.distance[1])]

        return (found == self.landmark[1])


class Menu(LargeVobj):
    all_menus = []

    # ALL LargeObj ARGS, dict of (String : Vobj|tuple(point, size)) -> Menu
    def __init__(self, lm, cmps={}, dst=(0, 0)):
        super().__init__(lm, dst)
        self._cmps       = cmps 
        Menu.all_menus.append(self)

    # String -> Vobj|tuple(point, size)
    # Return a clickable datatype from cmps dict
    def get(self, k):
        if k in self._cmps:
            cmp = self._cmps[k]
            
            match cmp:
                case Vobj():
                    return cmp
                case ((xdst, ydst), (w, h)):
                    return ((self.x + xdst, self.y + ydst), (w, h))
        else:
            raise Exception(k + " is not part of this Menu")
            
    ## None -> bool
    ## Return True  if current Menu is visible
    ##        False if not
    ## and update all the components location if the menu was found
    #def find(self):
    #    found = super().find()
    #    
    #    if found:
    #        for k, vo in self._cmps.items():
    #            match vo:
    #                case Vobj():
    #                    vo.find()
    #
    #
    #    return found
        
    # String, Vobj|tuple(point, size) -> None
    # Add/Edit given name and visual object in menu componenets
    def add(self, name, c):
        self._cmps[name] = c


    # None -> List of Menu
    # Find the current visible menus in context 
    def find_all_menus():
        return [menu for menu in all_menus if menu.find()]


class Table(LargeVobj):
    def __init__(self, lm, dst, sz, rc):
        super().__init__(lm, dst)
        self.size = sz
        self.rows, self.cols = rc
        self.xdst, self.ydst = self.size[0] // self.cols, self.size[1] // self.rows
    
    # int -> Point
    # return the location of an item in current table object
    def get(self, n):
        col = n % self.cols
        row = n // self.cols
        
        return ConstVobj((self.x + (col * self.xdst) - round(self.xdst * 0.25), 
                          self.y + (row * self.ydst) - round(self.ydst * 0.25)), 
                         (round(self.xdst * 0.25), 
                          round(self.ydst * 0.25)))
        
    # function, String -> None
    # Call given function according to given key "k"
    #   "BOTTOM_HALF" -> the bottom half of the table
    def do(self, actn, k):
        self.find()
        
        match k:
            case "BOTTOM_HALF":
                sind = self.rows * self.cols // 2
                find = self.rows * self.cols
        
        for i in range(sind, find):
            actn(self.get(i))
            
    
class DropList(LargeVobj):
    # ALL LargeObj ARGS, Size -> DropList
    def __init__(self, *args, sz):
        super().__init__(**args)
        self.size     = sz

    # int -> Point
    # Given an index of an item in a DropList
    # return the item's position on screen
    def get(index):
        repos = (self.width // 2, (self.height // 2) + (self.height * index))
        p = (self.x + repos[0], self.y + repos[1])

        return p


#-------------------------------------------------
# Classes :
#
# Menu is a compound datatype consisting of: 
# - landmark   : (Vobj, bool)
# - cmps : dict of {String:Vobj) 
#
# Interp. Represents a menu in a user interface
#           landmark -> is a pair of visual object and a boolean 
#                       that tells wether the menu is visible or not
#           cmps     -> a dict of all other visual objects that are contained
#                           inside the current menu
#
