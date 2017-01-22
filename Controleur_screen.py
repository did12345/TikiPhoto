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
from tikibooth_main import *

 ########## Functions

# Replacing ShowTapZones() with a more generic UpdateDisplay(). 
# When I'm done, ShowTapZones() will do exactly what it says. 
# Update display will take care of deciding which elements should be on screen.
def UpdateDisplay():
    global screen
    global background
    # Blit everything to the screen
    screen.blit(background, (0, 0))
    pygame.display.flip()
    logging.info('Display updated')
    return
# End of function
 
# Draws the Previous, Next, and Start tap zones on screen.
def ShowTapZones():
    global background
    background.fill(rgbBACKGROUND)  # Black background
    
	# Draw the Start tap zone on screen.
    pygame.draw.rect(background, rgbBLUE, pygame.Rect(START_MIN_X, START_MIN_Y, ZONEWIDTH, ZONEWIDTH))
    # pygame.draw.circle(screen, (0, 128, 255), (400, 240), 75)

    if ActiveScreen == 'init':
        background.blit(ImgPointLeft, (PREV_X, START_MIN_Y))
        background.blit(ImgPointRight, (NEXT_X, START_MIN_Y))
        background.blit(ImgOK, (START_MIN_X, START_MIN_Y))
    elif ActiveScreen == 'print':
		background.blit(ImgRestart, (PREV_X, START_MIN_Y))
		background.blit(ImgPrint, (NEXT_X, START_MIN_Y))

    if ShowInstructions == True:
        SetInstructions()

    SetEffectText(globalEffectList[globalEffectCurr])
    UpdateDisplay()
    return
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
    global background
    global smallfont
    Text = "TIKI PHOTO!!!"
    Text = smallfont.render(Text, 1, rgbRED)
    textpos = Text.get_rect()
    textpos.centerx = background.get_rect().centerx
    height = Text.get_height()
    background.blit(Text,(textpos)) #Write the small text
	
    Text = "APPUYER SUR OK POUR COMMENCER!"
    Text = smallfont.render(Text, 1, rgbRED)
    textpos = Text.get_rect()
    textpos.centerx = background.get_rect().centerx
    textpos.centery = height*2
    background.blit(Text, (textpos))  # Write the small text
    logging.info('Instructions set')
    return


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

def AfterPrintScreen():
    #defines the text of the printscreen and buttons
    ##text
    Text = "TIKIPHOTO REUSSI!"
	showTextMsg(Text, 'small', 5)
    return
# End of function.


# Permet d'afficher un texte au milieu de l'écran
def showTextMsg(text, font, size):
	if size == 'none': size = 3
	if font == 'big':
		text = bigfont.render(text, size, rgbRED)
	else:
		text = smallfont.render(text, size, rgbRED)
		
    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    textpos.centery = background.get_rect().centery
    background.blit(text, textpos)
    UpdateDisplay()
	

	
def PreviewMontageWAIT(MontageFile):
    logging.info("After printing...")
    preview = pygame.image.load(MontageFile)
    PILpreview = Image.open(MontageFile)
    previewSize = PILpreview.size # returns (width, height) tuple
    #added /1.5
    ScaleW = AspectRatioCalc(previewSize[0]/1.5, previewSize[1]/1.5, SCREEN_HEIGHT)
    preview = pygame.transform.scale(preview, (ScaleW, SCREEN_HEIGHT))
    SetBlankScreen()
    background.blit(preview, (SCREEN_WIDTH/2-ScaleW/2, 0))
    AfterPrintScreen()
    #inserting conditions here - get mouse
    camera.stop_preview()
    UpdateDisplay()
    sleep(1)
	
    ShowInstructions = True
    UpdateDisplay()
    return
    



# Aspect Ratio Calculator
def AspectRatioCalc(OldH, OldW, NewW):
    #(original height / original width) x new width = new height
    return int((OldH/OldW)*NewW)
# End of function.
