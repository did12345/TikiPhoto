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
from Controleur_print import *
from Controleur_screen import *
from tikibooth_main import *

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
    logging.info('Switching to effect ' + NewEffect)
    camera.image_effect = NewEffect
    globalEffectCurr = globalEffectList.index(NewEffect)
    SetEffectText(NewEffect)
	
	
# Writes the current effect to the screen using PyGame. 
def SetEffectText(NewEffect):
	global globalEffectDict
	Text = "Effect: " + globalEffectDict[NewEffect]
	showTextMsg(Text, 'small', 1)
	return