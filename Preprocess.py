import cv2
import numpy as np

win = (500,500)
big = ((80,80), (420,420))
small = ((150,150), (350,350))

def drawSquare(im, ((xo, yo), (x, y))):
    cv2.line(im, (xo,yo), (x,yo), (0,255,0))
    cv2.line(im, (x,yo), (x,y), (0,255,0))
    cv2.line(im, (x,y), (xo,y), (0,255,0))
    cv2.line(im, (xo,y), (xo,yo), (0,255,0))

def region(im):
    im[:big[0][0],:] = 0
    im[:,:big[0][1]] = 0
    im[big[1][0]:im.shape[1],:] = 0
    im[:,big[1][1]:im.shape[0]] = 0
    im[small[0][0]:small[1][0],small[0][1]:small[1][1]] = 0

def preprocess(im):
    #why do we cut the image again?
    im = np.array(im[:,:im.shape[0],:])
    im = cv2.resize(im, win)
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    
    edges = cv2.Canny(gray, 100, 240)

    drawSquare(im, big)
    drawSquare(im, small)
    
    region(edges)

    return edges, im
