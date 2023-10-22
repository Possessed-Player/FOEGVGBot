import numpy as np
from random        import uniform
from .clicker      import Clicker
from .utils        import sleep
from .visualobject import Vobj

    
class NatMouse(Clicker):
    def __init__(self, spd=20):
        super().__init__()
        self.MSP = spd
        self.sqrt3 = np.sqrt(3)
        self.sqrt5 = np.sqrt(5)
        
    # Point, String -> None
    # Move the mouse to some coordinates on screen in a human like way
    # Key "k" used to determine target location
    # "to" -> Just move cursor to given point
    # "by" -> Add given point to the current cursor location
    def move(self, p, k="to"):
        current = self.position()
        
        match k:
            case "to":
                target = p
            case "by":
                target = current[0] + p[0], current[1] + p[1]
        
        # Correct the coordinates if we're working on a window
        if Vobj.cm.iswin:
            target = (target[0] + Vobj.cm.x, target[1] + Vobj.cm.y)
            
                
        self._human_mouse(current[0], current[1], target[0], target[1])

    # int, int, int, int, *int, *int, *int, *int -> None
    # Makes the mouse movement human like
    #   G_0 - magnitude of the gravitational fornce
    #   W_0 - magnitude of the wind force fluctuations
    #   M_0 - maximum step size (velocity clip threshold)
    #   D_0 - distance where wind behavior changes from random to damped
    def _human_mouse(self, start_x, start_y, dest_x, dest_y, G_0=9, W_0=3, M_0=15, D_0=12):
        current_x,current_y = start_x,start_y
        v_x = v_y = W_x = W_y = 0
        while (dist:=np.hypot(dest_x-start_x,dest_y-start_y)) >= 1:
            W_mag = min(W_0, dist)
            if dist >= D_0:
                W_x = W_x/self.sqrt3 + (2*np.random.random()-1)*W_mag/self.sqrt5
                W_y = W_y/self.sqrt3 + (2*np.random.random()-1)*W_mag/self.sqrt5
            else:
                W_x /= self.sqrt3
                W_y /= self.sqrt3
                if M_0 < 3:
                    M_0 = np.random.random()*3 + 3
                else:
                    M_0 /= self.sqrt5
            v_x += W_x + G_0*(dest_x-start_x)/dist
            v_y += W_y + G_0*(dest_y-start_y)/dist
            v_mag = np.hypot(v_x, v_y)
            if v_mag > M_0:
                v_clip = M_0/2 + np.random.random()*M_0/2
                v_x = (v_x/v_mag) * v_clip
                v_y = (v_y/v_mag) * v_clip
            start_x += v_x
            start_y += v_y
            move_x = int(np.round(start_x))
            move_y = int(np.round(start_y))
            if current_x != move_x or current_y != move_y:
                #This should wait for the mouse polling interval
                super().move((current_x:=move_x,current_y:=move_y))

            wait = uniform(0, (100/self.MSP)) * 6
            
            if wait < (100 / self.MSP):
                wait = (100 / self.MSP)
                
            wait = (wait*0.9)/1000
            
            sleep(wait)


