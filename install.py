import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
	
if __name__ == "__main__":
	packages = ("pynput", 
			 	"numpy", 
			 	"mss",
				 "pywin32",
				"opencv-python",
				"pytesseract",
				)

	for p in packages:
		install(p)

	print("""\n\n 
	VERY IMPORTANT NOTE: THIS BOT/SCRIPT USES "bot_tools"
	   PYTHON PACKAGE, WHICH HAS AN OCR MODULE THAT RELIES
	   ON GOOGLE OCR "TESSERACT", IF THE BOT YOU'RE TRYING TO RUN
	   DOESN'T USE THIS FUTURE YOU WILL NOT NEED TO INSTALL ANYTHING ELSE,
	   ***BUT IN THE CASE IT DOES, IT WILL FAIL TO WORK PROPERLY
	   BECAUSE IT'S MISSING TESSERACT OCR, IF YOU'RE HAVING SUCH A PROBLEM
	   PLEASE TO REFER TO MY VIDEO ON HOW TO INSTALL TESSERACT-OCR 
	   \n\n""")