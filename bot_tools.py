import win32gui
import pyautogui as pag
import numpy as np
import cv2 as cv
import random as rnd
import threading
from pynput.keyboard import Listener
from pynput.mouse import Controller, Button


class Assistant:
	def __init__(self, win=False, name=""):
		self.on = True
		self.iswin = win
		self.x = None
		self.y = None
		self.w = None
		self.h = None
		if self.iswin: self.update_winfo(name)
			
		# Variables related to finding images on screen/window/image
		self.threshold = 0.8
		self.ismax = True
		self.method = "cv.TM_CCOEFF_NORMED"
		self.last_w = 0
		self.last_h = 0
		# Properties
		self._last_x = 0
		self._last_y = 0
		self.last_path = ""
		# Control
		self.fast_mouse = Controller()

	
	@property
	def last_x(self):
		if self.iswin:
			return self._last_x + self.x
		else:
			return self._last_x
	
	@property
	def last_y(self):
		if self.iswin:
			return self._last_y + self.y
		else:
			return self._last_y 


	# String -> None
	# Set a hotkey to start/stop running a while loop
	def on_off_htkey(self, key):
		kbd_thrd = threading.Thread(target=self.kb_listener, args=(key,))
		kbd_thrd.start()
		
		
	def kb_listener(self, k):
		def on_release(key):
			if str(key) == ("'" + k + "'"):
				self.on = not self.on

		with Listener(on_release=on_release) as listener:
			listener.join()
		

	# None -> None
	# 	Click on the last location found by image searching functions
	#	including functions that returns Boolean
	def click_on_last(self, rel="mid", t="left", times=1):
		self.click(self.last_x, self.last_y, rel, t, times) 
	

	# Integer, Integer, Integer, Integer -> None
	# Drag from first 2 given coordinates and adding to it
	# the next two given coordinates to be the place to darg to
	def drag_from_by(self, x, y, rel_x, rel_y, scnds=1, btn="left"):
		pag.moveTo(x, y)
		pag.drag(rel_x, rel_y, scnds, button=btn)
		
	# Integer, Integer -> None
	def move_to(self, x, y):
		pag.moveTo(x, y)

	
	# Integer, Integer, String, String, Integer, Float -> None
	# Clicks on given screen coordinates with or without relative
	# size and parts of the last found image on screen also specifying
	# with which button to click and times to click and delay between clicks
	def click(self, x=None, y=None, rel="tl", t="left", times=1, delay=0.25):
		if not x or not y:
			x, y = pag.position()
			delay = 0
			
		elif rel == "mid":
			x += (self.last_w // 2)
			y += (self.last_h // 2)
		elif rel == "r":
			x += rnd.randint(0, self.last_w)
			y += rnd.randint(0, self.last_h)

		pag.click(x, y, button=t, clicks=times, interval=delay) 


	# Integer, Integer -> None
	# Click on given x, y coordinates on screen
	# Using fast low level api
	def fast_click(self, x, y):
		self.fast_mouse.position = (x, y)
		self.fast_mouse.click(Button.left, 1)
		
	
	# String -> None	
	#	Load given image from path given as String
	#	Then find that image on screen or window
	#	Then click on it
	def findnclick_on(self, path):
		img = self.load_image(path)	
		res = self.find_img_onscreen(img)

		if res:
			self.click_on_last()

	
	# String -> (Float, (Integer, Integer)), None
	# Load image from given path and find it on screen
	def find_onscreen(self, path, one=True):
		img = self.load_image(path)

		self.last_path = path
		
		return self.find_img_onscreen(img, one)


	# BGR Image -> (Float, (Integer, Integer)), None
	# Finds given image on screen returns
	# minimum or maximum match score and location on screen
	# if found and return None if not found
	def find_img_onscreen(self, img, one=True):
		imga = img
		imgb = self.capture_screen()

		res = self.find_imga_in_imgb(imga, imgb, one)

		return res



	# BGR Image, BGR Image -> (Float, (Integer, Integer)), None
	#	Given ImageA and ImageB find ImageA in ImageB
	#	Return minimum or maximum match score
	#	along with the location on relative 
	def find_imga_in_imgb(self, imga, imgb, one=True):
		gimga = cv.cvtColor(imga, cv.COLOR_BGR2GRAY)
		gimgb = cv.cvtColor(imgb, cv.COLOR_BGR2GRAY)

		res = cv.matchTemplate(gimgb, gimga, eval(self.method))
		self.last_w, self.last_h = gimga.shape[::-1]
		diff = self.method in ["cv.TM_SQDIFF", "cv.TM_SQDIFF_NORMED"]
		min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)

		if one:
			if diff: 
				if min_val <= self.threshold:
					self._last_x = min_loc[0] 
					self._last_y = min_loc[1]
					return (min_val, min_loc)
				else:
					return None
			else:
				if max_val >= self.threshold:
					self._last_x = max_loc[0]
					self._last_y = max_loc[1]
					return (max_val, max_loc)
				else:
					return None
		else:
			if diff:
				loc = np.where(res <= self.threshold)
			else:
				loc = np.where(res >= self.threshold)

			points = []

			for pt in zip(*loc[::-1]): 
				points.append(pt)

			if points:
				return points
			else:
				return None	

		
		
	# Integer, Integer -> RGB(Integer, Integer, Integer)
	# Return the color of pixel x, y on screen
	def get_color(self, x, y):
		return pag.screenshot(region=(x, y, 1, 1)).getpixel((0, 0))
	
	
	# None -> Integer, Integer
	# Return mouse position on screen
	def mouse_position(self):
		return pag.position()
		
	
	# BGR Image, BGR Image -> Boolean
	#	Return True if imga is in imgb else return False
	def is_imga_in_imgb(self, imga, imgb):
		res = self.find_imga_in_imgb(imga, imgb)

		return bool(res)

	
	# String -> BGR Image
	#	Load image from given path and return the BGR Image
	def load_image(self, path):
		return cv.imread(path)
	

	# None -> BGR Image
	# Captures the screen and chooses whether
	# to use fullscreen or window based on
	# the current assistant
	def capture_screen(self):
		if self.iswin:
			return self._capture_window()
		else:
			return self._capture_full()

	# None -> BGR Image
	#	Captures screen in the region of the window
	#	and converts into BGR Image
	#	and return that image
	def _capture_window(self):
		pimg = pag.screenshot(region=(self.x, self.y, self.w, self.h))
		return self.process_image(pimg)	

	# None -> BGR Image
	# Capture the full screen and return it as BGR Image
	def _capture_full(self):
		pimg = pag.screenshot()
		return self.process_image(pimg)

	# String -> None 
	#	Find window by name in the current open windows
	#		Updates the object's x, y, w, h attributes
	#		if image is found
	def update_winfo(self, name):
		whnd = win32gui.FindWindowEx(None, None, None, name) 
		if whnd != 0:
			rect = win32gui.GetWindowRect(whnd) 
			self.x = rect[0]
			self.y = rect[1]
			self.w = rect[2] - self.x
			self.h = rect[3] - self.y

	# pag Image -> BGR Image
	#	Convert the given image form pag to BGR
	def process_image(self, pimg):
		pimg =  np.array(pimg)
		rgb = cv.cvtColor(pimg, cv.COLOR_RGBA2RGB)
		bgr = cv.cvtColor(rgb, cv.COLOR_RGB2BGR)

		return bgr
