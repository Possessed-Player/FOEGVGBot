import bot_tools as bt
from time import sleep
import sys
import re

DEFAULT_THRESH = 0.08
FILE = "res/"
MENU = "menu.png"
ATT_BTN = "aa_btn.png"
CNFRM_BTN = "win_btn.png"

# None -> Integer, Integer
# Click then find position of the menu that pops up
# on screen
def locate_menu():
	helper.click(times=2)
	sleep(0.5)
	helper.find_onscreen(FILE + MENU)
	return helper.last_x + 40, helper.last_y + 10
	

# None -> (Integer, Integer), (Integer, Integer, Integer), (Integer, Integer), (Integer, Integer)
#			(Integer, Integer, Integer)
# Find dialog button then collect position of empty slot and color, tab position, attack button
#	position and attack button position
def collect_dialog_data():
	while not helper.find_onscreen(FILE + ATT_BTN):
		sleep(0.5)
	aabtn_pos = (helper.last_x + 40, helper.last_y + 15)
	aabtn_clr = helper.get_color(aabtn_pos[0], aabtn_pos[1])
	slot_pos = (helper.last_x + 50, helper.last_y - 290)
	helper.click(slot_pos[0], slot_pos[1])
	sleep(0.5)
	slot_clr = helper.get_color(slot_pos[0], slot_pos[1])
	tab_pos = (helper.last_x - 90, helper.last_y - 205)
	helper.click(tab_pos[0] + 20, tab_pos[1] + 70)
	sleep(0.25)
	return slot_pos, slot_clr, tab_pos, aabtn_pos, aabtn_clr
	
	
# None -> (Integer, Integer), (Integer, Integer, Integer)
# Wait for the ok button to show up and then return
#	the ok button position and color
def collect_okbtn():
	while not helper.find_onscreen(FILE + CNFRM_BTN):
		sleep(0.5)
	okbtn_pos = (helper.last_x + 40, helper.last_y + 15)
	return okbtn_pos, helper.get_color(okbtn_pos[0], okbtn_pos[1])  
	
def main():
	while True:
		if helper.on:
			sect_pos = helper.mouse_position()
			if not NPC:
				men_pos = locate_menu()
				helper.click(men_pos[0], men_pos[1])
			else:
				helper.click(times=2)
			sleep(2)
			tab_dst = 45
			slot_pos, slot_clr, tab_pos, aabtn_pos, aabtn_clr = collect_dialog_data()
			helper.click(aabtn_pos[0], aabtn_pos[1])
			sleep(2)
			okbtn_pos, okbtn_clr = collect_okbtn()
			helper.click(okbtn_pos[0], okbtn_pos[1])
			sleep(2)
		while helper.on:
			clicked = False
			while helper.get_color(aabtn_pos[0], aabtn_pos[1]) != aabtn_clr:
				if not helper.on: break
				if not clicked:
					helper.fast_click(sect_pos[0], sect_pos[1])
					if not NPC:
						sleep(0.05)
						helper.fast_click(men_pos[0], men_pos[1])
					clicked = True
			
			if helper.get_color(slot_pos[0], slot_pos[1]) == slot_clr:
				helper.fast_click(tab_pos[0] + (45 * (TAB - 1)), tab_pos[1])
				if SLEEP: sleep(SLEEP[0])
				helper.fast_click(tab_pos[0] + 20, tab_pos[1] + 70)
				while helper.get_color(slot_pos[0], slot_pos[1]) == slot_clr:
					if not helper.on: break
					helper.fast_click(tab_pos[0] + 20, tab_pos[1] + 70)
					if SLEEP: sleep(SLEEP[0])
				
			
			helper.fast_click(aabtn_pos[0], aabtn_pos[1])
			
			while helper.get_color(okbtn_pos[0], okbtn_pos[1]) != okbtn_clr:
				if not helper.on: break
				if SLEEP: SLEEP[0]
				
			helper.fast_click(okbtn_pos[0], okbtn_pos[1])
			if SLEEP: sleep(SLEEP[1])


if __name__ == "__main__":
	global helper, SLEEP, TAB, NPC
	helper = bt.Assistant()
	helper.threshold = DEFAULT_THRESH
	helper.on_off_htkey("e")
	
	while True:
		ans = re.match("(1|2)", input("\n -- Choose one of the attacking options -- \n" + \
										"1. Player		2. NPC \n"))
		
		if ans:
			ans = ans.group(1)
			if ans == "1":
				NPC = False
			else:
				NPC = True
				
			break
			
	while True:
		ans = re.match("(1|2)", input("\n -- Choose one of the clicking speeds -- \n" + \
									"1. Fast		2. Very Fast \n"))
		if ans:
			ans = ans.group(1)
			if ans == "1":
				SLEEP = (0.0005, 0.001) 
			else:
				SLEEP = None
				
			break
			
	while True:
		ans = re.match("([1-6])", input("\n -- Type in the tab number to use troops from -- \n"))
		
		if ans:
			ans = ans.group(1)
			TAB = int(ans)
			
			break
			
	input("\n Hover the mouse on the sector to attack then press any key... \n")
	
	main()