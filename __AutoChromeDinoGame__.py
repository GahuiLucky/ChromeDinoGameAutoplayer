import cv2 as cv
import numpy as np
import ctypes
import imagesize as imsize
import pyautogui as gui
from mss import mss

def print_opencv_version(): #dosctring for opencv
    '''
    Checks the Version of OpenCV.
    '''
    print(cv.__version__)

def print_numpy_version(): #docstring for numpy
    '''
    Checks the Version of Numpy.
    '''
    print(np.version)

def print_mss_version():
    '''
    Checks the Version of mss.
    '''
    print(mss.__version__)

def get_monitors():
    '''
    Gets Monitor information.

    :param width: Gets the Pixelvalue of the width from the primary Monitor and returns them. 
    :param heigth: Gets the Pixelvalue of the heigth from the primary Monitor and returns them.  
    '''
    width, heigth = gui.size()[0], gui.size()[1]
    return width, heigth

def pushArray(newElement, array):
        '''
        Pushes every Element of the array one Index higher.
        Last Element gets lost.
        The newElement gets pushed on Index 0.

        :param newElement: New element which gets pushed in array.+
        
        :return array: The array which is operated with.
        '''
        length = len(array)-1
        for i in range(0, length+1):
            if i < length:
                array[length-i] = array[length-i-1]
            else:
                array[0] = newElement
        return array

def Cactus(array, CacName, CacValue):
    '''
    Decides which Cactus is the next Obstacle.

    :return CacName: The Obstacle Name.
    :return CacValue: The Obstacle Value.
    '''
    match max(array):
        case x if x > 14 and x < 18:
            CacName = "Small Cactus"
            CacValue = 1
        case x if x > 27 and x < 30:
            CacName = "Big Cactus"
            CacValue = 2
        case x if x > 35 and x < 45:
            CacName = "Triple Cacti"
            CacValue = 3
    return CacName, CacValue

def DinoJump(CacValue, Speed):
    '''
    Checks in which way the Trex needs to jump.

    :param CacValue: The CacValue shows which Cactus is in Front of the Trex.
    :param Speed: This Variable is the speed of the Game.
    '''
    match CacValue:
        case 1:
            gui.hotkey("Up")
        case 2:
            gui.hotkey("Up")
        case 3:
            gui.hotkey("Up")    
    return
def DayNight(Center, threshold):
    '''
    This function looks, if the Dino is running at day or night cyclus.

    :return True: Means that it is day.
    :return False: Means that it is night.
    '''
    if Center >= threshold:
        return True
    else:
        return False
def PicRead(PathArray):
    # width, height = imsize.get(PathArray[0])
    width, height = (100,100)
    CharArray = np.zeros(shape=(len(PathArray),height,width),
                         dtype=np.uint8)
    for i in range (0,len(PathArray)):
        Char = cv.imread(cv.samples.findFile(PathArray[i]),
                                 flags=cv.IMREAD_GRAYSCALE)   
        Char = cv.resize(Char, (width,height))
        _,Char = cv.threshold(Char, 0, 255, cv.THRESH_BINARY)     
        CharArray[i] = Char
        if (cv.waitKey(1) & 0xFF) == ord('q'):
            cv.destroyAllWindows()
            break
        
    return CharArray

    


def main():
    GamePaths = ["pictures/ChromeDinoGame.png"]
    CharPaths = ["pictures/trex.png",
             "pictures/small_cactus.png",
             "pictures/big_cactus.png",
             "pictures/two_big_cacti.png",
             "pictures/quad_cacti.png",
             "pictures/pterodactyl.png"]
    GameBoulder = PicRead(PathArray=GamePaths)
    Characters = PicRead(PathArray=CharPaths)
    print("Game = ", GameBoulder)
    print("Characters = ", Characters)
    CactusName = ""
    CactusValue = 0
    MonitorWidth, MonitorHeigth = get_monitors()
    bounding_box = {'top': 0, 'left': 1920, 'width': MonitorWidth, 'height': MonitorHeigth}
    boulder = np.zeros(shape=(10), dtype=float)
    sct = mss()
    orb = cv.ORB_create()
    while True:

        screen = np.array(sct.grab(bounding_box))
        game_org = screen[ (1080//2)-400  : (1080//2)+120,
                            (1920//2)-300 : (1920//2)+300,1]
        center = (game_org.shape[0]//2, game_org.shape[1]//2)
        background = game_org[center]
        print("shaope" , len(Characters))
        if background > 125:
            _,bnw = cv.threshold(game_org, 0, 255, cv.THRESH_OTSU | cv.THRESH_BINARY_INV)
            # for i in range(0, len(Characters)):
            #     _,Characters[i] = cv.threshold(Characters[i], 0, 255, cv.THRESH_OTSU | cv.THRESH_BINARY_INV)
        else:
            _,bnw = cv.threshold(game_org, 0, 255, cv.THRESH_OTSU | cv.THRESH_BINARY)
            # for i in range(0, len(Characters)-1):
            #     _,Characters[i] = cv.threshold(Characters[i], 0, 255, cv.THRESH_OTSU | cv.THRESH_BINARY_INV)
        
        player = bnw[center[0]//2 -55 : center[0]//2 +100,
                        center[1]-300 : center[1]-200]
        boulder_jump = bnw[center[0]//2 +25 : center[0]//2 +100,
                        center[1]-70 : center[1]]
        boulder_start = bnw[center[0]//2 +25 : center[0]//2 +100,
                        center[1]+150 : center[1]+220]

        newArray = pushArray(np.mean(boulder_jump), boulder)
        
        CactusName, CactusValue = Cactus(newArray, 
                                        CacName=CactusName,
                                        CacValue=CactusValue)
        # print("Maximum = ", max(newArray))
        # print("CactusName = ", CactusName)
        # print("CactusValue = ", CactusValue)
        kp1, des1 = orb.detectAndCompute(bnw,None)
        kp2, des2 = orb.detectAndCompute(Characters[0],None)
        bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1,des2)
        matches = sorted(matches, key = lambda x:x.distance)
        img3 = cv.drawMatches(bnw,kp1,Characters[0],kp2,matches[:10],None,flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
        cv.imshow("bnw", bnw)
        cv.imshow("test", img3)
        bnw = cv.putText(bnw, 
                        text=CactusName, 
                        org=(100,150),
                        fontFace=cv.FONT_HERSHEY_DUPLEX,
                        fontScale=0.5,
                        color=(255,255,255),
                        thickness=1)
        
        
        cv.imshow("char", Characters[2])
        # cv.imshow("player", player )
        # cv.imshow("boulder", boulder_jump )
        # cv.imshow("startboulder", boulder_start )
        # cv.imshow('screen', bnw)  

        if (cv.waitKey(1) & 0xFF) == ord('q'):
            cv.destroyAllWindows()
            break
if __name__ == "__main__":
    main()


