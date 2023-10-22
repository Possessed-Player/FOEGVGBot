from pynput.keyboard import Controller as kbd_ctrl
from pynput.keyboard import Key
from .utils import sleep

kbd = kbd_ctrl()

# String -> None
# Given a string type it using the keyboard
def type(s):
    for c in s:
        kbd.press(c)
        kbd.release(c)
        sleep(0.025)

# String -> None
# Press one key and release it immediately
def press(c):
    kbd.press(c)
    kbd.release(c)