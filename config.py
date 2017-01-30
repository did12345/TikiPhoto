#!/usr/bin/python
# -*- coding: utf-8 -*-
## configuration file for TIKIBOOTH
##
## (C) DIDIER HARDOIN <didier@hardoin.com>
## v 1.0
### Version: 2016-12-30

import os, time, sys

############################# Configuration Section.
# Preview Alpha, 0-255
PREVIEW_ALPHA = 120 # OK For Black Background
#PREVIEW_ALPHA = 140
#PREVIEW_ALPHA = 200 # Meh for White Background
#PREVIEW_ALPHA = 220
#PREVIEW_ALPHA = 240

# Set Screen Dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480

# Number of Photos to Take
NUMPHOTOS = 1
PhotoNumber = 0

# Camera Rotation
CAMROTATION = 0
CAMFREAMERATE = 15

# Width of previous and next tap zones.
# ZONEWIDTH = 100
ZONEWIDTH = 110

# Setup the Montage
# Pixels separating photos, maintain 2:3 aspect ratio. (Perfect for a 4"x6" print)
MONTAGESPACING_W = 30
MONTAGESPACING_H = 20
#MONTAGE_W = 1920
#MONTAGE_H = 2880
MONTAGE_W = 2048
MONTAGE_H= 1546

# PRINTER VARIABLES
PhotoResize = (512, 384)
PhotoTitle = "TIKI Photo Booth!"


########################### End of Configuration Section.
#Global variables

# RGB Codes
rgbRED = (255,0,0)
rgbGREEN = (0,255,0)
rgbBLUE = (0,0,255)
rgbDARKBLUE = (0,0,128)
rgbWHITE = (255,255,255)
rgbBLACK = (0,0,0)
rgbPINK = (255,200,200)
rgbGREY = (128,128,128)

# Background Color!
rgbBACKGROUND = rgbBLACK

####
# For readable code.
LEFTMOUSEBUTTON = 1

# Center of display.
CENTER_X = SCREEN_WIDTH/2
CENTER_Y = SCREEN_HEIGHT/2

# Previous Tap Zone: 0,0 to 100,480
# Previous Zone is easy, start at 0,0 (top left corner) and draw for ZONEWIDTH.
PREV_X = 0
PREV_Y = 0
# Next Tap Zone: 700,0 to 800,480
NEXT_X = SCREEN_WIDTH - ZONEWIDTH
NEXT_Y = SCREEN_HEIGHT

# Start Box, Center of Screen?
# Center: Width/2,Height/2.
# Upper left corner of box: CenterX-ZONEWIDTH/2,CenterY-ZONEWIDTH/2
START_MIN_X = CENTER_X-(ZONEWIDTH/1.5)
START_MAX_X = START_MIN_X+ZONEWIDTH
START_MIN_Y = CENTER_Y-(ZONEWIDTH/1.5)
START_MAX_Y = START_MIN_Y+ZONEWIDTH

# Define Up, Down, Left, Right, B, and A.
## Left is next to previous. Starts at PREV_X+ZONEWIDTH, ends at PREV_X+(ZONEWIDTH*2)
LEFT_MIN_X = PREV_X+ZONEWIDTH
LEFT_MAX_X = PREV_X+(ZONEWIDTH*2)
LEFT_MIN_Y = 0
LEFT_MAX_Y = SCREEN_HEIGHT

## Right is next to next. Starts at NEXT_X-ZONEWIDTH, Ends at NEXT_X.
RIGHT_MIN_X = NEXT_X-ZONEWIDTH
RIGHT_MAX_X = NEXT_X
RIGHT_MIN_Y = 0
RIGHT_MAX_Y = SCREEN_HEIGHT

# Up tap zone.
UP_MIN_X = LEFT_MIN_X
UP_MAX_X = RIGHT_MIN_X
UP_MIN_Y = 0
UP_MAX_Y = UP_MIN_Y + ZONEWIDTH

# Down tap zone.
DOWN_MIN_X = LEFT_MIN_X
DOWN_MAX_X = RIGHT_MIN_X
DOWN_MIN_Y = SCREEN_HEIGHT - ZONEWIDTH
DOWN_MAX_Y = SCREEN_HEIGHT


# List of effects to cycle through.
globalEffectList = ['none','sketch','posterise','emboss',
                    'watercolor','washedout','solarize','oilpaint']
# Dictionary of friendly names for the various effects.
globalEffectDict = {'none': 'Normal','sketch':'Artist Sketch','posterise':'Poster','emboss':'Embossed',
                    'negative':'Negative Zone','colorswap':'Swap Colors','hatch':'Crosshatch','watercolor':'Water Color',
                    'cartoon':'Cartoon','washedout':'Washed Out','solarize':'Solar Flare','oilpaint':'Oil Painting'}
# Current effect.
globalEffectCurr = 0
# Number of effects.
globalEffectLeng = len(globalEffectList)-1

# Photobooth SessionID
# When a session is in progress, touchscreen inputs are ignored. 
SessionID = 0

# Working Directory
globalWorkDir = '/home/pi/git/Tikiphoto'
LogoThumbnail = globalWorkDir + '/images/tikiphoto_thumb.jpg'
globalLogo = globalWorkDir + '/images/tikiphoto-r2.png'
globalEvent = 'test_Bru'
globalEVENTDir = globalWorkDir + '/' + globalEvent
globalDCIMDir = globalEVENTDir + '/DCIM'
#globalQRDir = globalEVENTDir + '/QR'
#globalThumbDir = globalEVENTDir + '/Thumb'

# Show instructions on screen?
ShowInstructions = True
LastTap = 0

##### Gestion DemoFlip
RESTART_TIME = 30
RunDemo = True
RunDemoCounter = time.time()
# Number of seconds between effect changes when the demo
DEMOCYCLETIME = 10

#Permet de connaitre l'ecran actif
#Valeurs possible : init / print
ActiveScreen = 'init'
LastScreen = ''

#Adresse de récupération des photos
URLEvent = "http://tphoto.hardoin.com/photos/"+globalEvent+"/"

#chemin de la dernière photo capturée
LastPhoto = ''
LastQR = ''
LastThumbnail = ''
QRSize = 150
ImpressionDone = False
