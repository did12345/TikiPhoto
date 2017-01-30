#!/usr/bin/python
# -*- coding: utf-8 -*-
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




def DemoFlip():
    global RunDemoCounter
    if (time.time()-RunDemoCounter >= DEMOCYCLETIME):
        NextEffect()
        RunDemoCounter = time.time()
# End of function.

# Generates a PhotoBoot Session
def SetupPhotobooth():
    global SessionID
    SessionID = int(time.time())  # Use UNIX epoc time as session ID.
    exist_ok = True
    logging.debug('Set photobooth session')
    if not os.path.exists(globalEVENTDir):
        os.makedirs(globalEVENTDir) 
    if not os.path.exists(globalDCIMDir):
        os.makedirs(globalDCIMDir)
		
def ReloadPhotobooth():
	global ShowInstructions
	global LastTap
	global RunDemo
	global ImpressionDone
	LastTap = 0
	ShowInstructions = True
	ImpressionDone = False
	RunDemo = True
	RunDemoCounter = time.time()
	SetEffect('none')
	logging.debug('PhotoBooth Session RESET!')
	StartCameraPreview()
# End of function.
		
def QuitGracefully():
    camera.stop_preview()
    camera.close()
    pygame.quit()
    logging.debug('Quit gracefully!')
    quit()
    #GPIO.remove_event_detect(BUTTON_NEXT)
    #GPIO.remove_event_detect(BUTTON_BACK)
    #GPIO.remove_event_detect(BUTTON_START)
    #GPIO.cleanup()
    #quit("Quitting program gracefully.")
# End of function


#chargement des images et mise à l'échelle
def initPicture(path, size=ZONEWIDTH):
	img = pygame.image.load(path)
	img = pygame.transform.scale(img, (ZONEWIDTH, ZONEWIDTH))
	return img
	
##################################################################################################################	
##########################################################CONTROLEUR BOUTON	######################################
##################################################################################################################
# Gestion de la zone de clic sur l'écran
def TouchScreen(xx, yy):
	logging.debug("clic - ActiveScreen %s", ActiveScreen)
	clickDone = True
	# Detect Taps in Previous Zone
	if xx >= PREV_X and xx <= ZONEWIDTH:
		logging.debug("Previous")
		TapPrev()
	# Detect Taps in Next Zone  
	elif xx >= NEXT_X and xx <= SCREEN_WIDTH:
		logging.debug("Next")
		TapNext()
	# Detect Taps in the Start Zone
	elif xx >= START_MIN_X and yy >= START_MIN_Y and xx <= START_MAX_X and yy <= START_MAX_Y:
		logging.debug("Start")
		TapStart()
    # Detect Taps in the Up Zone.
 #   elif xx >= UP_MIN_X and yy >= UP_MIN_Y and xx <= UP_MAX_X and yy <= UP_MAX_Y:
# 		loggin.info('UP')
	# Detect Taps in the Down Zone.
 #   elif xx >= DOWN_MIN_X and yy >= DOWN_MIN_Y and xx <= DOWN_MAX_X and yy <= DOWN_MAX_Y:
#		loggin.info('Down')
    # Detect Taps in the Left Zone.
 #   elif xx >= LEFT_MIN_X and yy >= LEFT_MIN_Y and xx <= LEFT_MAX_X and yy <= LEFT_MAX_Y:
#		loggin.info('Left')
    # Detect Taps in the Right Zone.
 #   elif xx >= RIGHT_MIN_X and yy >= RIGHT_MIN_Y and xx <= RIGHT_MAX_X and yy <= RIGHT_MAX_Y:
#		loggin.info('Right')"""
	else:
		logging.debug('Nothing')
		clickDone = False

	if clickDone:
		click()
		
		
		
		
# Function called when the Previous zone is tapped.
def TapPrev():
	if ActiveScreen=='init':
		logging.debug("prev effect")
		btnPrevEffect()
	elif ActiveScreen=='print':
		logging.debug("Preview screen option: restart")
		btnReload()
	else:
		doNothing('TapPrev')
	

# Function called when the Next zone is tapped.
def TapNext():
	if ActiveScreen=='init':
		logging.debug("next effect")
		btnNextEffect()
	elif ActiveScreen=='print':
		logging.debug("Preview screen")
		btnPrint()
	else:
		doNothing('TapNext')

		
# Function called when the Start zone is tapped.
def TapStart():
	if ActiveScreen=='init':
		logging.debug("Cheeeeeeeese")
		btnTakePicture()
	else:
		doNothing('TapStart')
		

def doNothing(zone):
	logging.debug("Do nothing on '%s' on this screen '%s'", zone, ActiveScreen)


		
	
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
	ReloadPhotobooth()
	ActiveScreen = 'init'

	
# Redirection vers la prise d'une photo
def btnTakePicture():
	global ActiveScreen
	global ShowInstructions
	#Capture de la photo
	RunPhotobooth()
	ActiveScreen = 'print'
	
	#affichage de la photo
	PreviewMontage(LastPhoto)
	camera.stop_preview()
	ShowInstructions = True
	Text = "TIKIPHOTO REUSSI!"
	showTextMsg(Text, 'small', 5, 'top')
	sleep(3)
	#Wait()
	

#Réinitialisation des variables à chaque clic sur l'ecran
def click():
	global RunDemo
	global LastTap
	global ShowInstructions
	RunDemo = False
	LastTap = time.time()
	ShowInstructions = False
	
##################################################################################################################
#########################################################CONTROLEUR CAMERA########################################
##################################################################################################################
#Lancement de l'appareil photo
def RunPhotobooth():
	global LastPhoto
	global LastQR
	global LastThumbnail
	currentPhoto = 1 # File name for photo.
	#SetupPhotobooth()
	logging.debug('Running PHOTOBOOTH SESSION')
	prefixe = time.strftime("%Y%m%d%H%M%s")
	PhotoPath = globalEVENTDir + '/%PhotoName%.jpg'
	while currentPhoto <= NUMPHOTOS:
		PhotoName = prefixe + "_" + str(currentPhoto) + globalEvent
		PhotoPathTmp = PhotoPath.replace('%PhotoName%', PhotoName)
		TakePhoto(PhotoPathTmp)
		currentPhoto = currentPhoto + 1

	numPhoto = 1
	while  numPhoto < currentPhoto:
		PhotoName = prefixe + "_" + str(numPhoto) + globalEvent
		PhotoMontageName = PhotoName + '_montage'
		PhotoQRName = PhotoName + '_QR.png'

		PhotoOriginalPath = PhotoPath.replace('%PhotoName%', PhotoName)
		PhotoMontagePath = PhotoPath.replace('%PhotoName%', PhotoMontageName)
		PhotoQRPath = PhotoPath.replace('%PhotoName%.jpg', PhotoQRName)

		logging.debug("Origine File: %s", PhotoOriginalPath)
		logging.debug("Montage File: %s", PhotoMontagePath)
		logging.debug("QR File: %s", PhotoQRPath)

		CreateMontage(PhotoMontagePath, PhotoOriginalPath)
		CopyMontageDCIM(PhotoMontagePath)
		CreateQRCode(PhotoQRPath, PhotoMontagePath)

		numPhoto = numPhoto + 1
		
	LastPhoto = PhotoOriginalPath
	LastQR = PhotoQRPath
	PhotoThumbnailName = PhotoName + '_THUMB'
	LastThumbnail = PhotoPath.replace('%PhotoName%', PhotoThumbnailName)
	CreateThumbnail(LastThumbnail, LastPhoto)

	
# Prise d'une photo
def TakePhoto(PhotoPath):
	RunCountdown()
	logging.debug('saving photo to: %s', PhotoPath)
	camera.stop_preview()
	camera.resolution = RES_PHOTO
	logging.debug('camera resolution: ')
	logging.debug(RES_PHOTO)
	camera.hflip = False
	Flash()
	camera.capture(PhotoPath)
	SetBlankScreen()
	#StartCameraPreview()

	
def RunCountdown():
	i = 5
	while i >= 0:
		if i == 0:
			string = 'CHEESE!!!'
		else:
			string = str(i)
		SetBlankScreen()
		showTextMsg(string, 'big', 1)
		i = i - 1
		sleep(1)
	# Blank Cheese off the screen.
	#SetBlankScreen()
	#UpdateDisplay()
	#return
# End of function.


def StartCameraPreview():
    camera.hflip = True
    camera.resolution = RES_PREVIEW
    camera.start_preview(alpha=PREVIEW_ALPHA)
    logging.debug('camera preview ON')
# End of function.



def CopyMontageDCIM(montageFile):
    global globalDCIMDir
    logging.debug('Creating MONTAGE DCIM')
	# Use copy not copyfile to copy a file to a directory.
    if os.path.isdir(globalDCIMDir):
        return shutil.copy(montageFile, globalDCIMDir)
        logging.debug('copying file to DCIMDIR %s', montageFile)
    else:
        return False

# End of function.


# Creates the Montage image using ImageMagick.
# Python ImageMagick bindings seem to suck, so using the CLI utility.
def CreateMontage(montageFile, originFile):
	logging.debug('Creating MONTAGE')
	#binMontage = '/usr/bin/montage'
	binMontage = '/usr/bin/convert'
	#    outFile = globalSessionDir + "/"+ time.strftime("%Y%m%d%H%M%S") + "_"+ globalEvent + ".jpg"
	#outFile = globalSessionDir + "/" + str(SessionID) + ".jpg"
	#argsMontage = "-tile 2x0 "
	#argsMontage = "-append " + "-background white -gravity center -smush -80 "

	argsMontage = originFile + " " + globalLogo
	argsMontage = argsMontage + " -background white -gravity south -smush -90 " + montageFile
	#argsMontage = argsMontage + "-gravity South -background white -chop 30x0 -delete 0,2 +swap -composite " + outFile
	logging.debug("Syntaxe montage")
	logging.debug(binMontage + " " + argsMontage)

	# Display Processing On screen.
	string = "Capture en cours"
	showTextMsg(string, 'small', 1)
	subprocess.call(binMontage + " " + argsMontage, shell=True)
	return montageFile
# End of function.

def CreateQRCode(QRCode, montageFile):
	#full name and path
	logging.debug('Creating QR')
	ArgsSystemQR= 'qrencode -l H -o '

	logging.debug("Syntaxe QR")
	logging.debug(ArgsSystemQR + QRCode + " " + montageFile)

	os.system(ArgsSystemQR + QRCode + " " + montageFile)
	logging.debug("QR CODE GENERATED %s", QRCode)
	return QRCode

##################################################################################################################
#########################################################CONTROLEUR EFFECTS ######################################
##################################################################################################################
########## Functions

# Affichage de l'effet suivant 
def NextEffect():
    global globalEffectCurr
    if globalEffectCurr == globalEffectLeng:
        globalEffectCurr = 0
    else:
        globalEffectCurr = globalEffectCurr + 1

	SetEffect(globalEffectList[globalEffectCurr])


# Affichage de l'effet précédant
def PrevEffect():
    global globalEffectCurr
    if globalEffectCurr == 0:
        globalEffectCurr = globalEffectLeng
    else:
        globalEffectCurr = globalEffectCurr - 1
		
    SetEffect(globalEffectList[globalEffectCurr])

	
# Function to change effect.
def SetEffect(NewEffect):
    global globalEffectCurr
    global camera
    logging.debug('Switching to effect ' + NewEffect)
    camera.image_effect = NewEffect
    globalEffectCurr = globalEffectList.index(NewEffect)
    SetEffectText(NewEffect)
	
	
# Writes the current effect to the screen using PyGame. 
def SetEffectText(NewEffect):
	global globalEffectDict
	Text = "Effect: " + globalEffectDict[NewEffect]
	showTextMsg(Text, 'small', 1, 'bottom')
	return
	
##################################################################################################################
#########################################################CONTROLEUR PRINT#########################################
##################################################################################################################
######## Functions

#Gestion de l'impression
def Printing():
	global ImpressionDone
	
	if ImpressionDone:
		string = "Impression deja effectuee"
		showTextMsg(string, 'small', 1)
		sleep(1)
	else:	
		#Display Processing On screen.
		string = "Impression en cours"
		showTextMsg(string, 'small', 1,'bottom')
		ImpressionDone = True

		Today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
		QRCode = LastQR
		
		#Creation du thumbnail
		Thumbnail = CreateThumbnail(LastThumbnail, LastPhoto)

		printer.wake()
		printer.begin(100) # Warmup time
		printer.setTimes(50000, 8000) # Set print and feed times
		printer.justify('C') # Center alignment
		printer.println(PhotoTitle)
		printer.println(Today)
		printer.feed(1) # Add a blank line
		printer.printImage(Image.open(Thumbnail), False) # Specify image to print
		#printer.feed(1) # Add a blank line
		printer.printImage(Image.open(LogoThumbnail), True) # Specify logo to print
		printer.printImage(Image.open(QRCode), False) #QRCode
		#printer.feed(1) # Add a few blank lines
		printer.println("Retrouve les photos sur:")
		printer.println(URLEvent)
		printer.feed(3) # Add a few blank lines
		printer.sleep()

		
def CreateThumbnail(Thumbnail, montageFile):
	logging.debug('Creating Thumbnail')
	# Generates the thumbnail for printing
	binMontage = '/usr/bin/convert'

	#TODO voir pour tourner la photo à l'horizontal
	# for reference PhotoResize = 512, 384
	#resize commands for reference: -brightness-contrast 45x25 -define jpeg:size=964x480
	ResizeCommands ="-define jpeg:size=964x480 " + montageFile + " -auto-orient -thumbnail 500x500  -brightness-contrast 10x0 -unsharp 0.5 -rotate 0 " + Thumbnail
	logging.debug(binMontage + " " + ResizeCommands)
	subprocess.call(binMontage + " " + ResizeCommands, shell=True)
	return Thumbnail
	
##################################################################################################################  
#########################################################CONTROLEUR SCREEN########################################
##################################################################################################################
########## Functions

# Replacing ShowTapZones() with a more generic UpdateDisplay(). 
# When I'm done, ShowTapZones() will do exactly what it says. 
# Update display will take care of deciding which elements should be on screen.
def UpdateDisplay():
	global screen
	global background
	global LastScreen
	LastScreen = ''
	# Blit everything to the screen
	screen.blit(background, (0, 0))
	pygame.display.flip()
	#logging.debug('Display updated')
	return
# End of function
 
# Draws the Previous, Next, and Start tap zones on screen.
def ShowTapZones():
	global LastScreen
	global background
	if ActiveScreen != LastScreen:
		background.fill(rgbBACKGROUND)  # Black background

		# pygame.draw.circle(screen, (0, 128, 255), (400, 240), 75)

		if ActiveScreen == 'init':
			background.blit(ImgPointLeft, (PREV_X, START_MIN_Y))
			background.blit(ImgPointRight, (NEXT_X, START_MIN_Y))
			# Draw the Start tap zone on screen.
			pygame.draw.rect(background, rgbBLUE, pygame.Rect(START_MIN_X, START_MIN_Y, ZONEWIDTH, ZONEWIDTH))
			background.blit(ImgOK, (START_MIN_X, START_MIN_Y))
			SetEffectText(globalEffectList[globalEffectCurr])
			
		elif ActiveScreen == 'print':
			#Affichage de la photo en fond
			PreviewMontage(LastPhoto)
			#Affichage des boutons
			background.blit(ImgRestart, (PREV_X, START_MIN_Y))
			background.blit(ImgPrint, (NEXT_X, START_MIN_Y))
			#Affichage du QRCode au milieu
			background.blit(initPicture(LastQR, QRSize), (CENTER_X-QRSize/2, CENTER_Y-QRSize/2))

		if ShowInstructions == True:
			if ActiveScreen == 'init':
				SetInstructions()
			elif ActiveScreen == 'print':
				SetInstructionsPrint()

		UpdateDisplay()
		LastScreen = ActiveScreen
# End of function

def SetBlankScreen():
    background.fill(rgbBACKGROUND)
    UpdateDisplay()
    return
# End of function. 

def Flash():
    background.fill(rgbWHITE)
    UpdateDisplay()
    return
# End of function. 

# Show the instructions on screen.
def SetInstructions():
	Text = "TIKI PHOTO!!!"
	showTextMsg(Text, 'small', 1, 'top')
	Text = "APPUYER POUR COMMENCER!"
	showTextMsg(Text, 'small', 1)
	
def SetInstructionsPrint():
	Text = "Instruction Print a faire"
	showTextMsg(Text, 'small', 1, 'top')

	
def PrintScreen():
	#defines the text of the printscreen and buttons
	#insert button for printing 
	pygame.draw.rect(background, rgbGREEN, pygame.Rect(NEXT_X, 0, ZONEWIDTH, SCREEN_HEIGHT))
	#restarting button
	pygame.draw.rect(background, rgbRED, pygame.Rect(PREV_X, PREV_Y, ZONEWIDTH, SCREEN_HEIGHT))
	##text
	text = "Imprimer ou recommencer?"
	showTextMsg(text, 'small', 3)
	return
# End of function.


# Permet d'afficher un texte au milieu de l'écran
def showTextMsg(text, font, size=3, positiony='center'):
	#if size == 'none': size = 3
	if font == 'big':
		text = bigfont.render(text, size, rgbRED)
	else:
		text = smallfont.render(text, size, rgbRED)
		
	textpos = text.get_rect()
	textpos.centerx = background.get_rect().centerx
	if positiony == 'top':
		textpos.centery = text.get_height()
	elif positiony == 'bottom':
		textpos.centery = SCREEN_HEIGHT - text.get_height()
	else:
		textpos.centery = background.get_rect().centery
	background.blit(text, textpos)
	UpdateDisplay()
	

# Affiche une image en arrière plan
def PreviewMontage(MontageFile):
	logging.debug("Preview Montage...")
	preview = pygame.image.load(MontageFile)
	PILpreview = Image.open(MontageFile)
	previewSize = PILpreview.size # returns (width, height) tuple
	#added /1.5
	ScaleW = AspectRatioCalc(previewSize[0]/1.5, previewSize[1]/1.5, SCREEN_HEIGHT)
	preview = pygame.transform.scale(preview, (ScaleW, SCREEN_HEIGHT))
	SetBlankScreen()
	background.blit(preview, (SCREEN_WIDTH/2-ScaleW/2, 0))
    



# Aspect Ratio Calculator
def AspectRatioCalc(OldH, OldW, NewW):
    #(original height / original width) x new width = new height
    return int((OldH/OldW)*NewW)
# End of function.


##################################################################################################################
######################################################### CONTROLEUR MAIN ########################################
##################################################################################################################

 # 2x up ; 4x down : TO QUIT 

sys.path.append("/home/pi/Python-Thermal-Printer")
from Adafruit_Thermal import *
printer = Adafruit_Thermal("/dev/serial0", 19200, timeout=5)
logging.basicConfig(filename='tiki-photo.log',level=logging.INFO)

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
ImgOK = initPicture(globalWorkDir + '/images/OK.png')

ImgPointLeft = initPicture(globalWorkDir + '/images/PointLeft.png')
ImgPointRight = initPicture(globalWorkDir + '/images/PointRight.png')

ImgPrint = initPicture(globalWorkDir + '/images/printer.png')
ImgRestart = initPicture(globalWorkDir + '/images/restart.png')

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


#SetEffect('none')
camera.resolution = RES_PREVIEW
camera.start_preview(alpha=PREVIEW_ALPHA)
sleep(2) # This seems to be recommended when starting the camera.

running = True
SetupPhotobooth()

while running:
	ShowTapZones()
	event = pygame.event.poll()
	#Fin du Programme
	if event.type == pygame.QUIT: 
		running = False
		raise SystemExit
	#Capture du click effectué
	elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFTMOUSEBUTTON:
		x, y = event.pos
		logging.debug("You pressed the left mouse button at (%d, %d)" % event.pos)
		TouchScreen(x, y)
	elif event.type == pygame.KEYDOWN:
		if event.key == pygame.K_F4:
			logging.debug('F4 pressed, quitting.')
			QuitGracefully()
	#elif event.type == pygame.MOUSEBUTTONUP and event.button == LEFTMOUSEBUTTON:
	#   logging.debug("You released the left mouse button at (%d, %d)" % event.pos)
	#Lancement du carousel de photos si aucun n'event n'est capturé
	
	elif RunDemo and ActiveScreen == 'init':
		DemoFlip()

	#Une fois le temps RESTART_TIME écoulé, on reinitialise
	if LastTap != 0 and time.time()-LastTap > RESTART_TIME:
		btnReload()
	
######################################################### End of Main