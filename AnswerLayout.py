import cv2
import numpy as np
from math import sqrt,ceil
from random import randint

#MAKE pageDims PERCENTAGES
#make sure to anti-alias circles
#puttext restricts minimum size to roughly 20px by 20px
#letters don't scale continuously

class Box:
    TL = TR = BL = BR = np.array([0,0], dtype=np.int)
    #lexicographically ordered list
    pList = []
    height = 0
    width = 0

    def __init__(self, TL, BR):
        if not (type(TL) == np.ndarray):
            TL = np.array(TL)
        if not (type(BR) == np.ndarray):
            BR = np.array(BR)

        #if the points are input in reverse order
        if TL.tolist()>BR.tolist():
            TL, BR = BR, TL
                
        self.TL = TL
        self.BR = BR
        self.TR = np.array([self.BR[0], self.TL[1]], dtype=np.int)
        self.BL = np.array([self.TL[0], self.BR[1]], dtype=np.int)

        self.pList = [self.TL, self.TR, self.BL, self.BR]

        self.width, self.height = BR-TL
   
    def empty(self):
        [xBool, yBool] = TL == BR
        return (xBool and yBool)

    def intersect(self, otherBox):
        #a is left of b
        if (self.BR[0] < otherBox.TL[0]):
            return False
        #a is right of b
        if (self.TL[0] > otherBox.BR[0]):
            return False
        #a is above b
        if (self.BR[1] < otherBox.TL[1]):
            return False
        #a is below b
        if (self.TL[1] > otherBox.BR[1]):
            return False

        #intersection
        return True;
    def draw(self, im, color, thickness):
        cv2.rectangle(im, tuple(self.TL), tuple(self.BR), color, thickness)

      
answerMap = {}

#debug
showBorder = False

'''GLOBALS'''
#drawing
font = cv2.FONT_HERSHEY_SIMPLEX
color = (0,0,0)
thickness = 4

#variables
letterSet = 'ABCDE'
questions = 44

'''listed in order of dependency'''

'''========Bubble Row Parameters========'''
#to increase bubble separation, increase length of rectangle (RectX)
#boudingRect is square enclosing single bubble
boundingRectX = 70
boundingRectY = 60
radius = int(round((0.7)*(boundingRectY/2)))

#offset to get from center of letter to its bottom left corner
letterCenterOffset = np.array([-int(round(0.4375*radius)), int(round(0.5*radius))], dtype=np.int)
'''====================================='''

'''========Global Positioning Parameters========'''
#using A4 ISO ratio, listed as [width, height]
pageHeight = 3000
pageDims = np.array([int(round(pageHeight/sqrt(2))), pageHeight], dtype=np.int)

#container is the box that we are searching for in the images
#TL is top left point, BR is bottom right point
#offset is a percentage of the whole image
containerTL = [int(round(0.05*pageHeight)),int(round(0.05*pageHeight))]
containerBR = [pageDims[0]-int(round(0.05*pageHeight)),pageDims[1]-int(round(0.4*pageHeight))]
container = Box(containerTL, containerBR)

containerMargTL = [container.TL[0]+int(round(container.TL[0]/2)),container.TL[1]+int(round(container.TL[1]/2))]
containerMargBR = [container.BR[0]-int(round(container.TL[0]/2)),container.BR[1]-int(round(container.TL[1]/2))]
containerMarg = Box(containerMargTL, containerMargBR)

#intra-aswerColumn metrics
#4*letterCenterOffset[0] because of two digits
numToFirstBubble = 3*radius
numToNextNum = 4*radius
questionWidth = len(letterSet)*boundingRectX + boundingRectY + 4*abs(letterCenterOffset[0]) + numToFirstBubble
questionHeight = numToNextNum

#first box containing an answer column
answerColTL = np.array([containerMarg.TL[0]+boundingRectY, containerMarg.TL[1]+boundingRectY], dtype=np.int)
answerColBR = answerColTL + np.array([questionWidth,containerMarg.height], dtype=np.int)
answerCol = Box(answerColTL, answerColBR)

IDTL = (containerMarg.BR[0]-answerCol.width, containerMarg.TL[1])
IDBR = (containerMarg.BR[0], container.TL[0]+int(containerMarg.height/3))
ID = Box(IDTL, IDBR)


#letter is a string of length 1
#letter center and circle center coincide, input is that center
def ndrawBubble(im, loc, letter, num):
    cv2.putText(im,letter,tuple(loc+letterCenterOffset), font, 1,color,thickness-1)
    cv2.circle(im,tuple(loc), radius, color, thickness)
    #change precision to manage division
    answerMap[(num, letter)] = loc.astype(float)/pageDims

#input position is the intersection of left wall of text and the centerline axis
def ndrawLetters(im, loc, num):
    for i in range(0,len(letterSet)):
        bubbLoc = loc+np.array([(i*boundingRectX)+(boundingRectX/2),0], dtype=np.int)
        ndrawBubble(im, bubbLoc, letterSet[i], num)
        p1 = loc+np.array([i*boundingRectX,-(boundingRectY/2)], dtype=np.int)
        p2 = loc+np.array([(i+1)*boundingRectX,(boundingRectY/2)], dtype=np.int)
        if showBorder:
            cv2.rectangle(im, tuple(p1), tuple(p2), color, thickness)

#number is stringified in function
#pass num all the way through to bubble drawer to put into answerMap
def ndrawNumberRow(im, loc, num):
    cv2.putText(im, str(num)+'.', tuple(loc+letterCenterOffset), font, 1, color,thickness-1)
    ndrawLetters(im, loc+np.array([numToFirstBubble,0], dtype=np.int), num)

#question range is a tuple of (starting point, end point), does not including end point
def ndrawAnswerColumn(im, loc, questionRange):
    for i in range(0,questionRange[1]-questionRange[0]):
        ndrawNumberRow(im, loc+np.array([0,(i*numToNextNum)], dtype=np.int), questionRange[0]+i)
    if showBorder:
        x,y = loc
        cv2.rectangle(im, (x-boundingRectY,y-boundingRectY), (x-boundingRectY+answerCol.width,min(containerMarg.BR[1],y-boundingRectY+answerCol.height)), (0,190,0), thickness) 

#draws borders of containers
def drawBorder(im):
    #container bounds
    container.draw(im, color, thickness+12)
    
    #container with margins added, removing boundingRect offset
    if showBorder:
        containerMarg.draw(im, color, thickness)
        
    #draw box containing student's ID
    ID.draw(im, color, thickness)

def ndrawBlank(im):
    #while you can fit answer columns in width wise, do so
    numCols = int(container.width/questionWidth)
    qsperCol = int(containerMarg.height/questionHeight)
    for i in range(0,numCols):
        #offset from first answerCol
        origin_i = answerCol.TL + np.array([i*answerCol.width,0], dtype=np.int)
        #if the ith answerColumn intersect the ID box, adjust it
        if ((origin_i[0]+questionWidth)>IDTL[0] and (origin_i[0]+questionWidth)<IDBR[0]):
            origin_i = np.array([origin_i[0], origin_i[1]+ID.height], dtype=np.int)
        qRange = (i*qsperCol,min((i+1)*qsperCol, questions))
        ndrawAnswerColumn(im, origin_i, qRange)
    return im

#answerMap make sure answerMap is generated before this is called
def generateTest(im, answerMap):
    for i in range(0, questions):
        (num, letter) = (i, letterSet[randint(0,len(letterSet)-1)])
        cv2.circle(im, tuple(np.round(pageDims*answerMap[(num, letter)]).astype(int)), radius, color, -1)
    return im

#initialize image and draw borders if parameter is set to True
#pageDims reversed for input
blank = 255*np.ones(pageDims[::-1])
drawBorder(blank)
blank = ndrawBlank(blank)
#blank_resized = cv2.resize(blank,(0,0), fx=0.25, fy=0.25)
#blank_resized = cv2.resize(blank,(1700,2200))
#cv2.imshow('blank', blank_resized)

test = generateTest(blank, answerMap)
test = cv2.resize(test,(0,0), fx=0.25, fy=0.25)
#cv2.imshow('test', test)
cv2.imwrite('test.jpg', test)


#waitkey(0) needed for stills
if cv2.cv.WaitKey(0) == 27:
    cv2.cv.DestroyAllWindows()
