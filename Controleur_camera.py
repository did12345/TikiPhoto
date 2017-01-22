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
from Controleur_bouton import *
from Controleur_effects import *
from Controleur_print import *
from Controleur_screen import *
from tikibooth_main import *

 ########## Functions

#Lancement de l'appareil photo
def RunPhotoboothSession():
	global LastPhoto
	global LastQR
	global ActiveScreen
	currentPhoto = 1 # File name for photo.
	#SetupPhotoboothSession()
	logging.info('Running PHOTOBOOTH SESSION')
	prefixe = time.strftime("%Y%m%d%H%M%s")
	PhotoPath = globalEVENTDir + '/%PhotoName%.jpg'
	while currentPhoto <= NUMPHOTOS:
		PhotoName = prefixe + "_" + currentPhoto + globalEvent
		PhotoPathTmp = PhotoPath.replace('%PhotoName%', PhotoName)
		TakePhoto(PhotoPathTmp)
		currentPhoto = currentPhoto + 1

	numPhoto = 1
	while  numPhoto < currentPhoto:
		PhotoName = prefixe + "_" + numPhoto + globalEvent
		PhotoMontageName = PhotoName + '_montage'
		PhotoQRName = PhotoName + '_QR.png'

		PhotoOriginalPath = PhotoPath.replace('%PhotoName%', PhotoName)
		PhotoMontagePath = PhotoPath.replace('%PhotoName%', PhotoMontageName)
		PhotoQRPath = PhotoPath.replace('%PhotoName%.jpg', PhotoQRName)

		logging.info("Origine File: %s", PhotoOriginalPath)
		logging.info("Montage File: %s", PhotoMontagePath)

		CreateMontage(PhotoOriginalPath, PhotoMontagePath)
		CopyMontageDCIM(PhotoMontagePath)
		CreateQRCode(PhotoQRPath, PhotoMontagePath)

		numPhoto = numPhoto + 1
		
	LastPhoto = PhotoOriginalPath
	LastQR = PhotoQRPath
	PhotoThumbnailName = PhotoName + '_THUMB'
	LastThumbnail = PhotoPath.replace('%PhotoName%', PhotoThumbnailName)
	PreviewMontageWAIT(PhotoMontagePath)
	ResetPhotoboothSession()
	ActiveScreen = 'print'

	
# Prise d'une photo
def TakePhoto(PhotoPath):
	RunCountdown()
	logging.info('saving photo to: ', PhotoPath)
	camera.stop_preview()
	camera.resolution = RES_PHOTO
	logging.info('camera resolution: ', RES_PHOTO)
	camera.hflip = False
	Flash()
	camera.capture(PhotoPath)
	SetBlankScreen()
	StartCameraPreview()

	
def RunCountdown():
	i = 5
	while i >= 0:
		if i == 0:
			string = 'CHEESE!!!'
		else:
			string = str(i)
		showTextMsg(string, 'big', 1)
		i = i - 1
		sleep(1)
	# Blank Cheese off the screen.
	SetBlankScreen()
	UpdateDisplay()
	return
# End of function.


def StartCameraPreview():
    camera.hflip = True
    camera.resolution = RES_PREVIEW
    camera.start_preview(alpha=PREVIEW_ALPHA)
    logging.info('camera preview ON')
# End of function.



def ResetPhotoboothSession():
    global SessionID
    SessionID = 0
    StartCameraPreview()
    SetEffect('none')
    logging.info('PhotoBooth Session RESET!')
# End of function.


def CopyMontageDCIM(montageFile):
    global globalDCIMDir
    # Use copy not copyfile to copy a file to a directory.
    if os.path.isdir(globalDCIMDir):
        return shutil.copy(montageFile, globalDCIMDir)
        logging.info('copying file to DCIMDIR ', montageFile)
    else:
        return False

# End of function.



# Creates the Montage image using ImageMagick.
# Python ImageMagick bindings seem to suck, so using the CLI utility.
def CreateMontage(originFile, montageFile):
	global globalSessionDir
	global SessionID
	global globalWorkDir
	logging.info('Creating MONTAGE')
	#binMontage = '/usr/bin/montage'
	binMontage = '/usr/bin/convert'
	#    outFile = globalSessionDir + "/"+ time.strftime("%Y%m%d%H%M%S") + "_"+ globalEvent + ".jpg"
	#outFile = globalSessionDir + "/" + str(SessionID) + ".jpg"
	#argsMontage = "-tile 2x0 "
	#argsMontage = "-append " + "-background white -gravity center -smush -80 "

	argsMontage = originFile + " " + globalWorkDir + globalLogo
	argsMontage = argsMontage + " -background white -gravity south -smush -90 " + montageFile
	#argsMontage = argsMontage + "-gravity South -background white -chop 30x0 -delete 0,2 +swap -composite " + outFile

	logging.info(binMontage + " " + argsMontage)

	# Display Processing On screen.
	string = "Processing, Please Wait."
	ShowTextMsg(string, 'small', 1)
	subprocess.call(binMontage + " " + argsMontage, shell=True)
	logging.info('montage file: ', montageFile)
# End of function.

def CreateQRCode(QRCode, montageFile):
    #full name and path
    ArgsSystemQR= 'qrencode -l H -o '
    os.system(ArgsSystemQR + QRCode + montageFile)
    logging.info("QR CODE GENERATED ", QRCode)