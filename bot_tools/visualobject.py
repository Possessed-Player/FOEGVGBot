# Vobj is a compound datatype
# with each of:
# - locations : List of pair of int
# - size      : pair of int or None
#
# Interp. Visual Object represent objects on screen where
#           objects must have a location and size and be able
#           to find it on screen. 
#
#
# <THIS CLASS IS INTENDED FOR FUTURE CLASSES TO USE AS A PARENT CLASS>
#
class Vobj:
    cm = None
    
    def __init__(self):
        self.locations = [[]]
        self.size      = None 

    def find(self):
        raise "Not Implemented"

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    @property
    def x(self):
        return self.locations[0][0]

    @property
    def y(self):
        return self.locations[0][1]
