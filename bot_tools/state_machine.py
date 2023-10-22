from threading import Thread, Lock, active_count, get_ident
from .utils    import sleep
#----------------------------------------------------------------
# Data Definitions:
#
# Input is a pair of:
# - String
# - Any Object 
#
# Interp. Represents one aspect of the state of the world
#
# Affect is one of:
# - "M"
# - "K"
# - "MK"
#
# Interp. Represents the type of input a Controller might affect
#           "M"  -> Mouse only
#           "K"  -> Keyboard only
#           "MK" -> Mouse and Keyboard
#           If a controller affects an input method other controllers
#               shouldn't use that input method because it might
#               their action output
#----------------------------------------------------------------
# Implementation details:
#
# Self-made state machine implementation created for video game botting
# but can be applicable in other areas.
#
# First you should define one or more Sensors with function which
# that interpret images and extract vital information from said images
# put all the Sensors into a list
#
# Also define one or more Controllers with Affect and 2 functions
# the first should check whether the Sensors outputs are normal for
# said Controller and return a bool, the second should act on the
# world if the Sensors output weren't normal
#
# Then define a Machine with a function that when called get the
# latest image of the world and the other 2 arguements are
# the list of Sensor and list of Controller you previously defined
#
# Start the state machine by calling the Machine you defined "operate"
# method 
#
# e.g.  snsrs   = [Sensor(sensing_function1), Sensor(sensing_function2)]
#       cntrlrs = [Controller("M", dv_function, act_function)]
#       gwf     = pyautogui.screenshot  # <-- function 
#       sm      = Machine(gwf, snsrs, cntrlrs)
#       sm.operate()
#
#----------------------------------------------------------------
class Machine:
    def __init__(self):
        self._is_on = [False]
        
    @property
    def is_on(self):
        return self._is_on[0]
    
    @is_on.setter
    def is_on(self, val):
        self._is_on[0] = val
        
    def stop(self):
        self.is_on = False
        
class StateMachine(Machine):
    def __init__(self, snsr, crlr, predata=[]):
        super().__init__()
        self.sensed     = False
        self.is_on      = False
        self.data       = {}
        self.sensor     = snsr
        self.sensor.connect(self._is_on, self.data)
        self.controller = crlr
        self.controller.connect(self._is_on, self.data)

    # None -> None
    # Stop the current state machine and reset
    def stop(self):
        self.is_on = False
        
        while active_count() > 1:
            sleep(0.25)
                
        self.data   = {}
        
    # dict(String:Any Object) -> None
    # Run the state machine on ready state
    def start(self, cs):
        self.is_on = True
        
        self.sensor.start(cs)
        self.controller.start(cs)


class Sensor(Machine):            
    def __init__(self, *dtctrs):
        super().__init__()
        # List of Detector
        self.detectors = dtctrs
        # Data bus
        self.data = None
    
    # [bool], {String:Any object} -> None
    # Called by the state machine to connect its on indicator
    # and data bus to this sensor
    # As a side effect sensor calls its detectors and connects
    # their data and on indicator as well
    def connect(self, sm_on, data):
        self._is_on = sm_on
        self.data   = data
        
        for detector in self.detectors:
            detector._is_on = self._is_on
            detector.data   = self.data
        
    # dict(String:Any object) -> None
    # Run all the input comliant detectors
    def start(self, cs):
        for detector in self.detectors:
            detector.start(cs)
        
class Detector(Machine):
    def __init__(self, df, rls={}):
        super().__init__()
        # None -> String, Any Object
        # Given world extract information based on the user-defined function
        self.detect = df
        # dict(String:Any object) used to determine whether to run
        # this detector or not based on the input
        self.rules = rls
        # Data bus
        self.data = None
    
    # {String:Any object}-> None
    # Check if given input matches this detector rules
    # run it if it does
    # return if not
    def start(self, cs):
        if self.data is None:
            raise Exception("Detector not connected to a data bus")
        else:
            for nm, val in self.rules.items():
                if cs[nm] != val:
                    return
            else:
                def helper():
                    while self.is_on:
                        self.detect(self.data)
                        sleep(0.25)
                        
                Thread(target=helper).start()


class Controller(Machine):
    MLOCK = Lock()
    KLOCK = Lock()
    prio_lst = {}
        
    def __init__(self, *acts):
        super().__init__()
        # list of Actuator
        self.actuators = acts
        # Data bus
        self.data = None
    
    # [bool], {String:Any object} -> None
    # Called by the state machine to connect its on indicator
    # and data bus to this Controller
    # As a side effect Controller calls its Actuators and connects
    # their data and on indicator as well
    def connect(self, sm_on, data):
        self._is_on = sm_on
        self.data   = data
        
        for actuator in self.actuators:
            actuator._is_on = self._is_on
            actuator.data   = self.data
            
    # {String:Any object} -> None
    # Run every actuator in this controller
    def start(self, cs):
        for actuator in self.actuators:
            actuator.start(cs)
            
class Actuator(Machine):
    def __init__(self, afc, getterf, prio, rls={}, msg=""):
        super().__init__()
        self.affect   = afc
        # dict of Input -> bool
        # Return True  : The world deviated from optimal state and the current
        #                controller should act
        #        False : The world is in optimal state from the 
        #                point of view of the current controller 
        # None -> None
        # Given input from sensors act on the world to restore optimal state 
        self.deviated, self.act = getterf()
        # Priority integer
        self.prio = prio
        # {String:Any Object} decides when should this actuator run
        self.rules = rls
        # String message to print when controller is in action
        self.msg = msg
        # Data bus
        self.data = None
        # Thread id
        self.id = None

    # Affect -> bool
    # Check if last affect and new affect cross in input method used
    def _affects_cross(self, afct):
        return len(set(afct).intersection(self.affect)) > 0
        
    # None -> None
    # Remove the current thread from the static shared priority list
    def remove_frm_prio(self):
        if self.id in Controller.prio_lst:
            del Controller.prio_lst[self.id]
                
    # Wait for self to have priority
    def _wait_prio(self):
        if self.has_deviated():
            Controller.prio_lst[self.id] = (self.prio, self.affect)
            sleep(0.25 * self.prio)
            
            top_prio = False if self.prio != 0 else True
            
            while not top_prio and self.is_on:
                for pri, aff in Controller.prio_lst.values():
                    if pri < self.prio and (self._affects_cross(aff)):
                        sleep(0.25)
                        break
                else:
                    top_prio = True
        else:
            self.remove_frm_prio()
            
    # Wait for the actuators using output methods to release the lock
    def _wait_lock_nrun(self):
        need_m = "M" in self.affect
        need_k = "K" in self.affect
        
        if need_m:
            Controller.MLOCK.acquire()
        if need_k:
            Controller.KLOCK.acquire()
        
        
        if self.has_deviated():
            self.act()
        else:
            self.remove_frm_prio()
            
        if need_m:
            Controller.MLOCK.release()
        if need_k:
            Controller.KLOCK.release()
        
        
    # None -> bool
    # Check whether the data bus deviated from baseline
    def has_deviated(self):
        return self.deviated(self.data)
        
    # {String:Any Object} -> None
    # Run the current actuator
    def start(self, cs):
        if self.data is None:
            raise Exception("Actuator started without a data bus")
        else:
            for nm, val in self.rules.items():
                if cs[nm] != val:
                    return
            else:
                def helper():
                    self.id = get_ident()
                    
                    while self.is_on:
                        self._wait_prio()
                        self._wait_lock_nrun()
                        sleep(0.25)
                
                Thread(target=helper).start()

