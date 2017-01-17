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
from config import * #configuration file
from PIL import Image
from time import sleep
from ftplib import FTP

 # 2x up ; 4x down : TO QUIT 

sys.path.append("/home/pi/Python-Thermal-Printer")
from Adafruit_Thermal import *
printer = Adafruit_Thermal("/dev/serial0", 19200, timeout=5)


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
ImgOK = pygame.image.load('images/OK.png')
ImgOK = pygame.transform.scale(ImgOK, (ZONEWIDTH, ZONEWIDTH))
ImgPointLeft = pygame.image.load('images/PointLeft.png')
ImgPointLeft = pygame.transform.scale(ImgPointLeft, (ZONEWIDTH, ZONEWIDTH))
ImgPointRight = pygame.image.load('images/PointRight.png')
ImgPointRight = pygame.transform.scale(ImgPointRight, (ZONEWIDTH, ZONEWIDTH))

ImgStart = pygame.image.load('images/8bit.png')
ImgStart = pygame.transform.scale(ImgStart, (ZONEWIDTH, ZONEWIDTH))
ImgA = pygame.image.load('images/A.png')
ImgA = pygame.transform.scale(ImgA, (ZONEWIDTH, ZONEWIDTH))
ImgB = pygame.image.load('images/B.png')
ImgB = pygame.transform.scale(ImgB, (ZONEWIDTH, ZONEWIDTH))

ImgPrint = pygame.image.load('images/printer.png')
ImgPrint = pygame.transform.scale(ImgPrint, (ZONEWIDTH, ZONEWIDTH))
ImgRestart = pygame.image.load('images/restart.png')
ImgRestart = pygame.transform.scale(ImgRestart, (ZONEWIDTH, ZONEWIDTH))
    
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
    return
# End of function
 
# Draws the Previous, Next, and Start tap zones on screen.
def ShowTapZones(KonamiScreen):
    global screen
    global background
    background.fill(rgbBACKGROUND)  # Black background
    # Draw the Previous tap zone on screen.
    #pygame.draw.rect(background, rgbBLUE, pygame.Rect(PREV_X, PREV_Y, ZONEWIDTH, SCREEN_HEIGHT))
    # Draw the Next tap zone on screen.
    # not drawing
    # pygame.draw.rect(background, rgbBLUE, pygame.Rect(NEXT_X, 0, ZONEWIDTH, SCREEN_HEIGHT))
    # Draw the Start tap zone on screen.
    pygame.draw.rect(background, rgbBLUE, pygame.Rect(START_MIN_X, START_MIN_Y, ZONEWIDTH, ZONEWIDTH))
    # pygame.draw.circle(screen, (0, 128, 255), (400, 240), 75)

    # If Up,Up,Down,Down,Left,Right,Left,Right has been successfully entered,
    # the tap zone icons change to B, A, and an alien guy.
    if KonamiScreen == True:
        background.blit(ImgB, (PREV_X, START_MIN_Y))
        background.blit(ImgA, (NEXT_X, START_MIN_Y))
        background.blit(ImgStart, (START_MIN_X, START_MIN_Y))
    else:
        background.blit(ImgPointLeft, (PREV_X, START_MIN_Y))
        background.blit(ImgPointRight, (NEXT_X, START_MIN_Y))
        background.blit(ImgOK, (START_MIN_X, START_MIN_Y))

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
    return

def ButtonsPrint():
    global background
    global smallfont
#    Text = "IMPRIMER!"
#    Text = smallfont.render(Text, 1, rgbRED)
#    #height = Text.get_height()
#    textpos = Text.get_rect()
#    textpos.midleft = background.get_rect().midleft
#    background.blit(Text, (textpos))
#    
#    Text = "Recomencer!"
#    Text = smallfont.render(Text, 1, rgbBLACK)
#    textpos = Text.get_rect()
#    textpos.midright = background.get_rect().midright
#    background.blit(Text, (textpos))
    background.blit(ImgRestart, (PREV_X, START_MIN_Y))
    background.blit(ImgPrint, (NEXT_X, START_MIN_Y))
    
    return
#end of function BUTTONS PRINT
        

# Writes the current effect to the screen using PyGame. 
def SetEffectText(NewEffect):
    global globalEffectDict
    global background
    global smallfont
    #Text = "Effect: " + globalEffectDict[NewEffect]
    Text = "Effect: " + globalEffectDict[NewEffect]
    Text = smallfont.render(Text, 1, rgbRED)
    textpos = Text.get_rect()
    textpos.centerx = background.get_rect().centerx
    textpos.centery = SCREEN_HEIGHT - Text.get_height()
    background.blit(Text,(textpos)) #Write the small text
    #UpdateDisplay()
    return

def QuitGracefully():
    camera.stop_preview()
    camera.close()
    pygame.quit()
    quit()
    #GPIO.remove_event_detect(BUTTON_NEXT)
    #GPIO.remove_event_detect(BUTTON_BACK)
    #GPIO.remove_event_detect(BUTTON_START)
    #GPIO.cleanup()
    #quit("Quitting program gracefully.")
# End of function

# Call on an input event that resets Konami Code.
def KonamiCodeReset():
    global globalKonamiLast
    print('Konami Code Reset!')
    globalKonamiLast = 'None'
    return

# If the Konami Code is verified, then fire!
def KonamiCodeVerified():
    print('Konami Code Verified!!!')
    QuitGracefully()
    return

# Call on an input event that is part of Konami Code.
def KonamiCode(KonamiInput):
    global globalKonamiLast
    # 2x up ; 4x down
    # Up 1, Up 2, Down 1, Down 2, Left 1, Right 1, Left 2, Right 2, B, A.
    if KonamiInput == 'Up' and globalKonamiLast == 'None':
        globalKonamiLast = 'Up1'
        Sequence = True  
    elif KonamiInput == 'Up' and globalKonamiLast == 'Up1':
        globalKonamiLast = 'Up2'
        Sequence = True
    elif KonamiInput == 'Down' and globalKonamiLast == 'Up2':
        globalKonamiLast = 'Down1'
        Sequence = True
    elif KonamiInput == 'Down' and globalKonamiLast == 'Down1':
        globalKonamiLast = 'Down2'
        Sequence = True
    elif KonamiInput == 'Down' and globalKonamiLast == 'Down2':
        globalKonamiLast = 'Down3'
        Sequence = True
#    elif KonamiInput == 'Right' and globalKonamiLast == 'Left1':
#        globalKonamiLast = 'Right1'
#        Sequence = True
#    elif KonamiInput == 'Left' and globalKonamiLast == 'Right1':
#        globalKonamiLast = 'Left2'
#        Sequence = True
#    elif KonamiInput == 'Right' and globalKonamiLast == 'Left2':
#        globalKonamiLast = 'Right2'
#        Sequence = True
#    elif KonamiInput == 'B' and globalKonamiLast == 'Right2':
#        globalKonamiLast = 'B'
#        Sequence = True
#    elif KonamiInput == 'A' and globalKonamiLast == 'B':
#        globalKonamiLast = 'A'
#        Sequence = True
    elif KonamiInput == 'Down' and globalKonamiLast == 'Down3':
        KonamiCodeVerified()
        Sequence = True
    else:
        KonamiCodeReset()
        Sequence = False
    print(KonamiInput)
    return Sequence
# End of function.

# Process Input from the Left Mouse Button being depressed.
# Also tapping on the touch screen.
def LeftMouseButtonDown(xx, yy):
    # Detect Taps in Previous Zone
    if xx >= PREV_X and xx <= ZONEWIDTH:
        if KonamiCode('B') == False:
            TapPrev()
            return
#     Detect Taps in Next Zone  
    if xx >= NEXT_X and xx <= SCREEN_WIDTH:
        if KonamiCode('A') == False:
            TapNext()
        elif KonamiCode('A') == True:
            print("NEXT IT IS CAPTAIN")
    # Detect Taps in the Start Zone
    if xx >= START_MIN_X and yy >= START_MIN_Y and xx <= START_MAX_X and yy <= START_MAX_Y:
        if KonamiCode('Start') == False:
            TapStart()
    # Detect Taps in the Up Zone.
    elif xx >= UP_MIN_X and yy >= UP_MIN_Y and xx <= UP_MAX_X and yy <= UP_MAX_Y:
        KonamiCode('Up')
    # Detect Taps in the Down Zone.
    elif xx >= DOWN_MIN_X and yy >= DOWN_MIN_Y and xx <= DOWN_MAX_X and yy <= DOWN_MAX_Y:
        KonamiCode('Down')
    # Detect Taps in the Left Zone.
    elif xx >= LEFT_MIN_X and yy >= LEFT_MIN_Y and xx <= LEFT_MAX_X and yy <= LEFT_MAX_Y:
        KonamiCode('Left')
    # Detect Taps in the Right Zone.
    elif xx >= RIGHT_MIN_X and yy >= RIGHT_MIN_Y and xx <= RIGHT_MAX_X and yy <= RIGHT_MAX_Y:
        KonamiCode('Right')
    else:
        KonamiCodeReset()
        print("No Event")
    return
# End of function.

# Function to change effect.
def SetEffect(NewEffect):
    global globalEffectList
    global globalEffectCurr
    global camera
    print('Switching to effect ' + NewEffect)
    camera.image_effect = NewEffect
    SetEffectText(NewEffect)
    globalEffectCurr = globalEffectList.index(NewEffect)
    return
# End of function.

# Function to begin 
def NextEffect():
    global globalEffectList
    global globalEffectCurr
    if SessionID != 0:
        return False
    if globalEffectCurr == globalEffectLeng:
        globalEffectCurr = 0
    else:
        globalEffectCurr = globalEffectCurr + 1
    NextEff = globalEffectList[globalEffectCurr]
    SetEffect(NextEff)
    #added to test
    if SessionID > 0:
        ResetPhotoboothSession()
        SetupPhotoboothSession()
        IdleReset()
        UpdateDisplay()
        return False
    print ("print button on the left! we got it")
    
# End of function.



# Function to cycle effects backward.
def PrevEffect():
    global globalEffectList
    global globalEffectCurr
    if SessionID != 0:
        return False
    if globalEffectCurr == 0:
        globalEffectCurr = globalEffectLeng
    else:
        globalEffectCurr = globalEffectCurr - 1
    NextEff = globalEffectList[globalEffectCurr]
    SetEffect(NextEff)
    if SessionID > 0:
        print ("print button on the previous zone! we got it")
        ResetPhotoboothSession()
        SetupPhotoboothSession()
        IdleReset()
        UpdateDisplay()
        return False
    return True
 #End of Function

# Generates a PhotoBoot Session
def SetupPhotoboothSession():
    global SessionID
    global globalWorkDir
    global globalSessionDir
    SessionID = int(time.time())  # Use UNIX epoc time as session ID.
    # Create the Session Directory for storing photos.
    #globalSessionDir = globalWorkDir + '/' + str(SessionID)
    globalSessionDir = globalSessionDir
    #os.makedirs(globalSessionDir, exist_ok=True)
    exist_ok=True
    if not os.path.exists(globalSessionDir):
        os.makedirs(globalSessionDir) 

# End of function

def StartCameraPreview():
    camera.hflip = True
    camera.resolution = RES_PREVIEW
    camera.start_preview(alpha=PREVIEW_ALPHA)
# End of function.

def TakePhoto(PhotoNum):
    global SessionID
    global globalSessionDir
    PhotoNum = PhotoNum + 1
    PhotoPath = globalSessionDir + '/' + str(PhotoNumber) + "_" + globalEvent + '.jpg'
    camera.stop_preview()
    camera.resolution = RES_PHOTO
    camera.hflip = False
    # Feeling ambitions? PyGame the screen to white, turn off camera preview, take picture, change back to normal.
    background.fill(rgbWHITE)
    UpdateDisplay()
    camera.capture(PhotoPath)
    background.fill(rgbBACKGROUND)
    UpdateDisplay()
    StartCameraPreview()
# End of function.

def RunCountdown():
    i = 5
    while i >= 0:
        if i == 0:
            string = 'CHEESE!!!'
        else:
            string = str(i)
        text = bigfont.render(string, 1, rgbRED)
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        textpos.centery = background.get_rect().centery
        SetBlankScreen()
        background.blit(text, (textpos))
        UpdateDisplay()
        i = i - 1
        sleep(1)
    # Blank Cheese off the screen.
    SetBlankScreen()
    UpdateDisplay()
    return
# End of function.

def ResetPhotoboothSession():
    global SessionID
    SessionID = 0
    StartCameraPreview()
    SetEffect('none')
# End of function.

def CopyMontageDCIM(montageFile):
    global globalDCIMDir
    # Use copy not copyfile to copy a file to a directory.
    if os.path.isdir(globalDCIMDir):
        return shutil.copy(montageFile,globalDCIMDir)
        
    else:
        return False

# End of function.

def RunPhotoboothSession():
    global NUMPHOTOS
    currentPhoto = 1 # File name for photo.
    SetupPhotoboothSession()
    while currentPhoto <= NUMPHOTOS:
        RunCountdown()
        TakePhoto(currentPhoto)
        currentPhoto = currentPhoto + 1
    outFile = globalSessionDir + "/"+ time.strftime("%Y%m%d%H%M") + "_"+ globalEvent + ".jpg"
    montageFile = CreateMontage(outFile)
    CopyMontageDCIM(montageFile)
    print("Montage File: " + montageFile)
    PreviewMontage(montageFile, outFile)
    ResetPhotoboothSession()
# End of function.

# Function called when the Start zone is tapped.
def TapStart():
    global RunDemo
    print("Start")
    RunDemo = False
    # I think this will clear the screen?
    background.fill(rgbBACKGROUND)
    UpdateDisplay()
    RunPhotoboothSession()
    #sleep(10)
    return
# End of Function.

# Function called when the Previous zone is tapped.
def TapPrev():
    global RunDemo
    RunDemo = False
    global ShowInstructions
    global LastTap
    print("Previous")
    ShowInstructions = False
    LastTap = time.time()
    if SessionID > 0:
        print("Preview screen option: restart")
        ResetPhotoboothSession()
        UpdateDisplay()
        SetBlankScreen()
        SetupPhotoboothSession()
        StartCameraPreview()
        UpdateDisplay()
        IdleReset()
    else:
        PrevEffect()
        print("prev effect")
    return
# End of Function

# Function called when the Next zone is tapped.
def TapNext():
    global SessionID
    global ShowInstructions
    global LastTap
    global RunDemo
    RunDemo = False
    print("Next")
    ShowInstructions = False
    LastTap = time.time()
    if SessionID > 0:
        print("Preview screen option: Print")
        PrintResize()
        #Printing()   
    else:
        NextEffect()
        print("next effect")
    return
# End of Function

def IdleReset():
    global ShowInstructions
    global LastTap
    global RunDemo
    LastTap = 0
    ShowInstructions = True
    RunDemo = True
    RunDemoCounter = 0
    SetEffect('none')
    UpdateDisplay()
# End of function.


# Creates the Montage image using ImageMagick.
# Python ImageMagick bindings seem to suck, so using the CLI utility.
def CreateMontage(outFile):
    global globalSessionDir
    global SessionID
    global globalWorkDir
    #binMontage = '/usr/bin/montage'
    binMontage = '/usr/bin/convert'
#    outFile = globalSessionDir + "/"+ time.strftime("%Y%m%d%H%M%S") + "_"+ globalEvent + ".jpg"
    #outFile = globalSessionDir + "/" + str(SessionID) + ".jpg"
    #argsMontage = "-tile 2x0 "
    #argsMontage = "-append " + "-background white -gravity center -smush -80 "
    argsMontage = ""
    # Loop controls.
    incrementCounter = True
    photoCounter = 1
    #argsMontage = argsMontage + globalWorkDir + "/images/Logo.png " + globalWorkDir + "/images/Logo.png "
    #argsMontage = argsMontage + globalWorkDir + "/images/Logo.png " 
    #argsMontage = argsMontage + str(globalSessionDir) + "/" + str(photoCounter) + "_" + globalEvent + '.jpg'

    argsMontage = argsMontage + str(globalSessionDir) + "/" + str(PhotoNumber) + "_" + globalEvent + '.jpg'
    argsMontage = argsMontage + " " + globalWorkDir + globalLogo
    argsMontage = argsMontage + " -background white -gravity south -smush -90 " + outFile
    #argsMontage = argsMontage + "-gravity South -background white -chop 30x0 -delete 0,2 +swap -composite " + outFile
    print(binMontage + " " + argsMontage)
    # Display Processing On screen.
    string = "Processing, Please Wait."
    
    text = smallfont.render(string, 1, rgbRED)
    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    textpos.centery = background.get_rect().centery
    SetBlankScreen()
    background.blit(text, textpos)
    UpdateDisplay()
    subprocess.call(binMontage + " " + argsMontage, shell=True)
    return outFile
    #return
# End of function.


def PreviewMontage(MontageFile, outFile):
    #attention MAJUSCULE "M"
#    global SessionID
#    SessionID = 0
    global LastTap
    LastTap = time.time()
    print("Session ID:", SessionID)
    print("Show something.")
    preview = pygame.image.load(MontageFile)
    PILpreview = Image.open(MontageFile)
    previewSize = PILpreview.size # returns (width, height) tuple
    #added /1.5
    ScaleW = AspectRatioCalc(previewSize[0]/1.5, previewSize[1]/1.5, SCREEN_HEIGHT)
    preview = pygame.transform.scale(preview, (ScaleW, SCREEN_HEIGHT))
    SetBlankScreen()
    background.blit(preview, (SCREEN_WIDTH/2-ScaleW/2, 0))
    PrintScreen()
    #inserting conditions here - get mouse
    camera.stop_preview()
    UpdateDisplay()
#    PrintResize()
#    print("montage file preview M: " ,MontageFile)
#    print("montage file preview m: " ,montageFile)
    ImageName = outFile.split("/")[-1]
    QRName = ImageName.replace(".jpg", "_QR.png")
    
    print('ImageName: ' ,ImageName)
    print ('QRName : ' ,QRName)
    QRCode = MontageFile.replace(ImageName, QRName)
    print ('QRCode:' ,QRCode)
    #full name and path
    ArgsSystemQR= 'qrencode -l H -o '
    URL = ' http://tphoto.hardoin.com/photos/nouvel-an-2017/'
    os.system(ArgsSystemQR + QRCode + URL + ImageName)
    print ("QR CODE GENERATED ", QRCode)
    Wait()
    #sleep(20)
    return 

def PreviewMontageWAIT(MontageFile):
#    global SessionID
#    SessionID = 0
    global LastTap
    LastTap = time.time()
    print("After printing...")
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
#    ResetPhotoboothSession()
#    SetupPhotoboothSession()
#    UpdateDisplay()
    ShowInstructions = True
    UpdateDisplay()
    return
    

def PrintScreen():
    #defines the text of the printscreen and buttons
    #insert button for printing 
    pygame.draw.rect(background, rgbGREEN, pygame.Rect(NEXT_X, 0, ZONEWIDTH, SCREEN_HEIGHT))
    #restarting button
    pygame.draw.rect(background, rgbRED, pygame.Rect(PREV_X, PREV_Y, ZONEWIDTH, SCREEN_HEIGHT))
    ##text
    text = "Imprimer ou recommencer?"
    text = smallfont.render(text, 3, rgbRED)   
    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    textpos.centery = background.get_rect().centery
    background.blit(text, textpos)
    UpdateDisplay()
    ButtonsPrint()

    return
# End of function.

def AfterPrintScreen():
    #defines the text of the printscreen and buttons
    ##text
    Text = "TIKIPHOTO REUSSI!"
    Text = smallfont.render(Text, 5, rgbRED)   
    textpos = Text.get_rect()
    textpos.centerx = background.get_rect().centerx
    textpos.centery = background.get_rect().centery
    background.blit(Text, textpos)
    return
# End of function.

#def uploadFTP(montageFile):
#    print ('upload image: ' ,montageFile)
#    #FTP UPLOAD
#    ftp = FTP('ftp.cluster007.hosting.ovh.net')
#    ftp.login(user='hardoinctj', passwd = '8rC54HU6AU6W92gr')
#    ftp.cwd('/tphoto/photos/nouvel-an-2017/') 
#    ftp.storbinary('STOR '+montageFile, open(montageFile, 'rb'))    # send the file          
#    ftp.quit()
#    QRName = 'QR-' + outFile
#    ImageName = outFile
#    print ('QRName : ' ,QRName)
#    QRCode = 'qr-' + montageFile #full name and path
#
#    ArgsSystem= 'qrencode -l H -o'
#    URL = 'http://tphoto.hardoin.com/photos/nouvel-an-2017/'
#
#    os.system(QRCode + URL + ImageName)
#    print ("QR CODE GENERATED ", QRCode)
#    return

def Wait():
    clock = pygame.time.Clock()
    waiting = True
    time2=5500
    while waiting:
        clock.tick(time2)
        #time2 = 60
        #dt = clock.tick(30) / 1000  # Takes the time between each loop and convert to seconds.
        #time2 -= dt
        time2 = time2 -1 
        #print("Waiting..", waiting, "time ", time2)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFTMOUSEBUTTON:
                x, y = event.pos
                print("You pressed the left mouse button at (%d, %d)" % event.pos)
                LeftMouseButtonDown(x, y)
                waiting = False
                sleep(1)

        if time2 == 0:
            waiting = False
#  
    return

######## PRINTING
def Printing():
    QRCode = Thumbnail.replace("_THUMB.jpg", "_QR.png")
    print ("Print option initiated!!!!!")
    Today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    # Generate the thumbnail for printing
    #PrintResize()
    # Rotate the thumbnail for printing ok 
        # Print the foto
    printer.wake()
    printer.begin(100) # Warmup time
    printer.setTimes(50000, 8000) # Set print and feed times
    printer.justify('C') # Center alignment
    printer.println(PhotoTitle)
    printer.println(Today)
    printer.feed(1) # Add a blank line
    print('ThumbGlobal: ' ,Thumbnail)
    printer.printImage(Image.open(Thumbnail), True) # Specify image to print
    #printer.feed(1) # Add a blank line
    print('Logothumb: ', LogoThumbnail)
    printer.printImage(Image.open(LogoThumbnail), True) # Specify logo to print
    printer.printImage(Image.open(QRCode), True) #QRCODE
    #printer.printImage(Image.open(photoPath + "qr-code.png"), True) # Specify image to print
    #printer.feed(1) # Add a few blank lines
    printer.println("Trouve les photos de l'evenement sur:")
    printer.println("http://tphoto.hardoin.com/photos/nouvel-an-2017/")
    #printer.printBarcode("TIKIPHOTO", printer.CODE39)
    #printer.println("TIKI-PHOTO SUR FACEBOOK!")
    printer.feed(2) # Add a few blank lines
    printer.sleep()
    #os.system('mv ' + QRCode + ' ' + DestQR)
    #os.system('mv ' + Thumbnail + ' ' + DestThumb)
#  
         #Display Processing On screen.
    string = "Processing, Please Wait."
    text = smallfont.render(string, 1, rgbRED)
    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    textpos.centery = background.get_rect().centery
    SetBlankScreen()
    background.blit(text, textpos)
    UpdateDisplay()
    #subprocess.call(binMontage + " " + argsMontage, shell=True)
    PreviewMontageWAIT(Thumbnail)
    #sleep(3)
    


def PrintResize():
    # Generates the thumbnail for printing
    global Thumbnail
    binMontage = '/usr/bin/convert'
    ActualPhoto= str(globalSessionDir) + "/" + str(PhotoNumber) + "_" + globalEvent + '.jpg'
    ActualLogo= str(globalSessionDir) + "/" + str(globalLogo)
    Thumbnail= str(globalSessionDir) + "/" + time.strftime("%Y%m%d%H%M") + "_" + globalEvent + "_THUMB" + '.jpg'
    QRCode = Thumbnail.replace("_THUMB.jpg", "_QR.png")
    #Thumbnail = ThumbnailGlobal
    # for reference PhotoResize = 512, 384
    #resize commands for reference: -brightness-contrast 45x25 -define jpeg:size=964x480
    ResizeCommands ="-define jpeg:size=964x480 " + ActualPhoto + " -auto-orient -thumbnail 500x500  -brightness-contrast 10x0 -unsharp 0.5 -rotate 270 " + Thumbnail
    print(binMontage + " " + ResizeCommands)
    subprocess.call(binMontage + " " + ResizeCommands, shell=True)
    print("resizing done")
    print ("thumbnail:  ", Thumbnail)
    Printing()
    return Thumbnail

# Aspect Ratio Calculator
def AspectRatioCalc(OldH, OldW, NewW):
    #(original height / original width) x new width = new height
    return int((OldH/OldW)*NewW)
# End of function.

#togo = custom.TIMELAPSE - (time.time() - last_snap) 
#def slideshow()
#    global LastTap
#    LastTap = time.time()
#    ScaleW = AspectRatioCalc(previewSize[0]/1.5, previewSize[1]/1.5, SCREEN_HEIGHT)
#    preview = pygame.transform.scale(preview, (ScaleW, SCREEN_HEIGHT))
#    SetBlankScreen()
#    background.blit(preview, (SCREEN_WIDTH/2-ScaleW/2, 0))
#	if (time.time() - 7 > LastTap and time.time() - 7 > LastTap):
#		last_image_swap = time.time()
#		filenames = next(os.walk(globalDCIMDir))[2]
#		count = randint(1,len(filenames))
#		count = count - 1
#		print (count)
#		filename = filenames[count]
#		print (filename)
#		im = Image.open(globalDCIMDir + filename)
#		display_image(im)
#		print ('no button pressed, looping')
#        
#        preview = pygame.image.load(MontageFile)
#        PILpreview = Image.open(MontageFile)
#        previewSize = PILpreview.size # returns (width, height) tuple
#    #added /1.5
#
#    PrintScreen()

########## End of functions.

def DemoFlip():
    global RunDemo
    global RunDemoCounter
    if (time.time()-RunDemoCounter >= DEMOCYCLETIME):
        NextEffect()
        RunDemoCounter = time.time()
# End of function.

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
RunDemoCounter = time.time()

while running:
    event = pygame.event.poll()
    #event = pygame.event.get()
    if event.type == pygame.QUIT:
        running = 0
        raise SystemExit
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFTMOUSEBUTTON:
        x, y = event.pos
        print("You pressed the left mouse button at (%d, %d)" % event.pos)
        LeftMouseButtonDown(x, y)
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_F4:
            print('F4 pressed, quitting.')
            QuitGracefully()
    #elif event.type == pygame.MOUSEBUTTONUP and event.button == LEFTMOUSEBUTTON:
    #   print("You released the left mouse button at (%d, %d)" % event.pos)
    elif RunDemo:
        DemoFlip()


    if LastTap != 0 and time.time()-LastTap > IDLETIME:
        IdleReset()

    if globalKonamiLast == 'A' or globalKonamiLast == 'B' or globalKonamiLast == 'Right2':
        ShowTapZones(True)
    else:
        ShowTapZones(False)
########## End of Main

