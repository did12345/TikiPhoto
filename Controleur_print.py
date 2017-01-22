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
from Controleur_camera import *
from Controleur_effects import *
from Controleur_screen import *
from tikibooth_main import *

######## Functions

#Gestion de l'impression
def Printing():
	# Generates the thumbnail for printing
	global Thumbnail
	logging.info('Resizing for print: ' ,Thumbnail)

	binMontage = '/usr/bin/convert'
	ActualPhoto = LastPhoto
	ActualLogo = str(globalEVENTDir) + "/" + str(globalLogo)
	Thumbnail = LastThumbnail
	QRCode = LastQR

	# for reference PhotoResize = 512, 384
	#resize commands for reference: -brightness-contrast 45x25 -define jpeg:size=964x480
	ResizeCommands ="-define jpeg:size=964x480 " + ActualPhoto + " -auto-orient -thumbnail 500x500  -brightness-contrast 10x0 -unsharp 0.5 -rotate 270 " + Thumbnail
	logging.info(binMontage + " " + ResizeCommands)
	subprocess.call(binMontage + " " + ResizeCommands, shell=True)

	Today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
	# Generate the thumbnail for printing
	# Rotate the thumbnail for printing ok 
		# Print the foto
	printer.wake()
	printer.begin(100) # Warmup time
	printer.setTimes(50000, 8000) # Set print and feed times
	printer.justify('C') # Center alignment
	printer.println(PhotoTitle)
	printer.println(Today)
	printer.feed(1) # Add a blank line
	printer.printImage(Image.open(Thumbnail), True) # Specify image to print
	#printer.feed(1) # Add a blank line
	printer.printImage(Image.open(LogoThumbnail), True) # Specify logo to print
	printer.printImage(Image.open(QRCode), True) #QRCODE
	#printer.printImage(Image.open(photoPath + "qr-code.png"), True) # Specify image to print
	#printer.feed(1) # Add a few blank lines
	printer.println("Retrouve les photos de l'evenement sur:")
	printer.println(URLEvent)
	#printer.printBarcode("TIKIPHOTO", printer.CODE39)
	#printer.println("TIKI-PHOTO SUR FACEBOOK!")
	printer.feed(2) # Add a few blank lines
	printer.sleep()
	#os.system('mv ' + QRCode + ' ' + DestQR)
	#os.system('mv ' + Thumbnail + ' ' + DestThumb)

	#Display Processing On screen.
	string = "Processing, Please Wait."
	showTextMsg(string, 'small', 1)

	#subprocess.call(binMontage + " " + argsMontage, shell=True)
	PreviewMontageWAIT(Thumbnail)
	#sleep(3)
	return Thumbnail
  