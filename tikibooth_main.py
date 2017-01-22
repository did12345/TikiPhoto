## TIKI PHOTO BOOOTH
## (C) DIDIER HARDOIN <didier@hardoin.com>
## v 1.0
### Version: 2016-12-30
from __future__ import print_function
import picamera
import pygame
import os, time, sys
import shutil
import subprocess
import datetime
import logging
from config import * #configuration file
from PIL import Image
from time import sleep
from ftplib import FTP
from Controleur_bouton import *
from Controleur_camera import *
from Controleur_effects import *
from Controleur_print import *
from Controleur_screen import *

 # 2x up ; 4x down : TO QUIT 

sys.path.append("/home/pi/Python-Thermal-Printer")
from Adafruit_Thermal import *
printer = Adafruit_Thermal("/dev/serial0", 19200, timeout=5)
logging.basicConfig(filename='tiki-photo.log',level=logging.DEBUG)

## Initialise PyGame
# pygame.mixer.pre_init(44100, -16, 1, 1024*3) #PreInit Music, plays faster
pygame.init() # Initialise pygame
# Don't full screen until you have a way to quit the program. ;)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),pygame.FULLSCREEN)
pygame.display.set_caption('TIKI Booth')

# Setup the game surface
background = pygame.Surface(screen.get_size())
background = background.convert()
background.fill(rgbBACKGROUND)

# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# pygame.mouse.set_visible(False)
# Working around what seems to be a bug in PyGame and/or libsdl where the
# cursor gets stuck in the lower right corner of the Raspberry Pi touchscreen
# after a few taps. This only happens when the cursor is not visible in PyGame Fullscreen.
# My workaround is setting a very small cursor. 
pygame.mouse.set_visible(True)
pygame.mouse.set_cursor((8, 8), (4, 4), (24, 24, 24, 231, 231, 24, 24, 24), (0, 0, 0, 0, 0, 0, 0, 0))

# Load images and scale them to the screen and tap zones. 
# At some point find a GO! or START! icon that works with the transparency and all that. 
ImgOK = util.initPicture('images/OK.png')
ImgA = util.initPicture('images/A.png')
ImgB = util.initPicture('images/B.png')

ImgPointLeft = util.initPicture('images/PointLeft.png')
ImgPointRight = util.initPicture('images/PointRight.png')
ImgStart = util.initPicture('images/8bit.png')

ImgPrint = util.initPicture('images/printer.png')
ImgRestart = util.initPicture('images/restart.png')

# Fonts to be used.
smallfont = pygame.font.Font(None, 50) #Small font for on screen messages.
# Original: 180
bigfont = pygame.font.Font(None, 220) # Big font for countdown.

# Working around what seems to be a bug in PyGame and/or libsdl where the
# cursor gets stuck in the lower right corner of the Raspberry Pi touchscreen
# after a few taps. This only happens when the cursor is not visible in PyGame Fullscreen.
# My workaround is setting a very small cursor. 
#pygame.mouse.set_visible(True)
#pygame.mouse.set_cursor((8, 8), (4, 4), (24, 24, 24, 231, 231, 24, 24, 24), (0, 0, 0, 0, 0, 0, 0, 0))
########## End of Settings/Globals.

########## Object Initializations.
camera = picamera.PiCamera()
camera.rotation = CAMROTATION
camera.framerate = CAMFREAMERATE


# Flip the camera horizontally so it acts like a mirror.
camera.hflip = True

######### Main

# Setup Camera resolution for picture taking.
# PiCam Max Res is 2592, 1944, a 4:3 aspect ratio.
# A 4x6 print (4 inch height, 6 inch width) is 3:2 aspect ratio.
# This gives us ready to use thumbnails to montage, minimal scaling needed.
CAMRES_W = int((MONTAGE_W/2)-(MONTAGESPACING_W*2))
#CAMRES_W = 
# Maintain the Aspect Ratio Math:
# (original height / original width) x new width = new height
#CAMRES_H = AspectRatioCalc(1920, 2880, CAMRES_W)
CAMRES_H=480
RES_PREVIEW = (640, 480)
RES_PHOTO = (CAMRES_W, CAMRES_H)


SetEffect('none')
camera.resolution = RES_PREVIEW
camera.start_preview(alpha=PREVIEW_ALPHA)
sleep(2) # This seems to be recommended when starting the camera.

running = 1
SetupPhotoboothSession()

while running:
	
	ShowTapZones()
	
	event = pygame.event.poll()
	"""Fin du Programme"""
    if event.type == pygame.QUIT: 
        running = 0
        raise SystemExit
	"""Capture du click effectué"""
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFTMOUSEBUTTON:
        x, y = event.pos
        logging.info("You pressed the left mouse button at (%d, %d)" % event.pos)
        TouchScreen(x, y)
    """elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_F4:
            logging.info('F4 pressed, quitting.')
            QuitGracefully()"""
    #elif event.type == pygame.MOUSEBUTTONUP and event.button == LEFTMOUSEBUTTON:
    #   logging.info("You released the left mouse button at (%d, %d)" % event.pos)
	"""Lancement du carousel de photos si aucun n'event n'est capturé"""
	elif RunDemo:
        DemoFlip()

    if LastTap != 0 and time.time()-LastTap > IDLETIME:
        IdleReset()
	
########## End of Main

def DemoFlip():
    global RunDemoCounter
    if (time.time()-RunDemoCounter >= DEMOCYCLETIME):
        NextEffect()
        RunDemoCounter = time.time()
# End of function.

# Generates a PhotoBoot Session
def SetupPhotoboothSession():
    global SessionID
    global globalWorkDir
    global globalSessionDir
    SessionID = int(time.time())  # Use UNIX epoc time as session ID.
    # Create the Session Directory for storing photos.
    #globalSessionDir = globalWorkDir + '/' + str(SessionID)
    #os.makedirs(globalSessionDir, exist_ok=True)
    exist_ok = True
    logging.info('Set photobooth session')
    if not os.path.exists(globalSessionDir):
        os.makedirs(globalSessionDir) 
		
		
def QuitGracefully():
    camera.stop_preview()
    camera.close()
    pygame.quit()
    logging.info('Quit gracefully!')
    quit()
    #GPIO.remove_event_detect(BUTTON_NEXT)
    #GPIO.remove_event_detect(BUTTON_BACK)
    #GPIO.remove_event_detect(BUTTON_START)
    #GPIO.cleanup()
    #quit("Quitting program gracefully.")
# End of function

def IdleReset():
    global ShowInstructions
    global LastTap
    global RunDemo
    logging.info('IDLE RESET!!')
    LastTap = 0
    ShowInstructions = True
    RunDemo = True
    RunDemoCounter = 0
    SetEffect('none')
    UpdateDisplay()
# End of function.

#chargement des images et mise à l'échelle
def initPicture(path):
	img = pygame.image.load(path)
	img = pygame.transform.scale(img, (ZONEWIDTH, ZONEWIDTH))
return img