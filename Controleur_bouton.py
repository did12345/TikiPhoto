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
from Controleur_camera import *
from Controleur_effects import *
from Controleur_print import *
from Controleur_screen import *
from tikibooth_main import *

# Gestion de la zone de clic sur l'écran
def TouchScreen(xx, yy):
	clickDone = true
    # Detect Taps in Previous Zone
    if xx >= PREV_X and xx <= ZONEWIDTH:
		logging.info("Previous")
		TapPrev()
	# Detect Taps in Next Zone  
    elif xx >= NEXT_X and xx <= SCREEN_WIDTH:
		logging.info("Next")
		TapNext()
    # Detect Taps in the Start Zone
    elif xx >= START_MIN_X and yy >= START_MIN_Y and xx <= START_MAX_X and yy <= START_MAX_Y:
		logging.info("Start")
		TapStart()
"""    # Detect Taps in the Up Zone.
    elif xx >= UP_MIN_X and yy >= UP_MIN_Y and xx <= UP_MAX_X and yy <= UP_MAX_Y:
		loggin.info('UP')
	# Detect Taps in the Down Zone.
    elif xx >= DOWN_MIN_X and yy >= DOWN_MIN_Y and xx <= DOWN_MAX_X and yy <= DOWN_MAX_Y:
		loggin.info('Down')
    # Detect Taps in the Left Zone.
    elif xx >= LEFT_MIN_X and yy >= LEFT_MIN_Y and xx <= LEFT_MAX_X and yy <= LEFT_MAX_Y:
		loggin.info('Left')
    # Detect Taps in the Right Zone.
    elif xx >= RIGHT_MIN_X and yy >= RIGHT_MIN_Y and xx <= RIGHT_MAX_X and yy <= RIGHT_MAX_Y:
		loggin.info('Right')"""
    else:
		loggin.info('Nothing')
		clickDone = false
	
	if clickDone:
		util.click()

		
		
		
		
# Function called when the Previous zone is tapped.
def TapPrev():
    if ActiveScreen=='init':
        logging.info("prev effect")
        btnPrevEffect()
    elif ActiveScreen=='print':
		logging.info("Preview screen option: restart")
		btnReload()
	else:
        doNothing('TapPrev')
	

# Function called when the Next zone is tapped.
def TapNext():
	if ActiveScreen=='init':
        logging.info("next effect")
        btnNextEffect()
    elif ActiveScreen=='print':
        logging.info("Preview screen")
        btnPrint()
    else:
        doNothing('TapNext')

		
# Function called when the Start zone is tapped.
def TapStart():
	if ActiveScreen=='init':
        logging.info("Cheeeeeeeese")
		btnTakePicture()
	else:
        doNothing('TapStart')
		

def doNothing(zone):
	logging.info("Do nothing on '%s' on this screen '%s'", zone, ActiveScreen)




		
	
# Redirection vers la gestion du previousEffect	
def btnPrevEffect():
	PrevEffect()	

	
# Redirection vers la gestion du nextEffect	
def btnNextEffect():
	NextEffect()	

	
# Redirection vers la gestion de l'impression	
def btnPrint():
	Printing()


# Redirection vers l'initialisation	
def btnReload():
	global ActiveScreen
	"""ResetPhotoboothSession()
	UpdateDisplay()
	SetBlankScreen()
	#SetupPhotoboothSession()
	StartCameraPreview()
	UpdateDisplay()"""
	IdleReset()
	ActiveScreen = 'init'

	
# Redirection vers la prise d'une photo
def btnTakePicture():
	# I think this will clear the screen?
	background.fill(rgbBACKGROUND)
	UpdateDisplay()
	RunPhotoboothSession()
	#sleep(10)
	
	

#Réinitialisation des variables à chaque clic sur l'ecran
def click():
	global RunDemo
    global LastTap
    global ShowInstructions
    RunDemo = False
    LastTap = time.time()
    ShowInstructions = False
	
