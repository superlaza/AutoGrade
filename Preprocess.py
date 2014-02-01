import cv2
import numpy as np

def drawSquare(im, ((xo, yo), (x, y))):
    cv2.line(im, (xo,yo), (x,yo), (0,255,0))
    cv2.line(im, (x,yo), (x,y), (0,255,0))
    cv2.line(im, (x,y), (xo,y), (0,255,0))
    cv2.line(im, (xo,y), (xo,yo), (0,255,0))

def region(im, big, small):
    im[:big[0][0],:] = 0
    im[:,:big[0][1]] = 0
    im[big[1][0]:im.shape[1],:] = 0
    im[:,big[1][1]:im.shape[0]] = 0
    im[small[0][0]:small[1][0],small[0][1]:small[1][1]] = 0

def preprocess(im, win, sbig, ssmall):
    im = np.array(im[:,:im.shape[0],:])
    im = cv2.resize(im, win)
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    
    edges = cv2.Canny(gray, 100, 240)

    temp = cv2.dilate(edges, np.ones((3,3)), iterations=4)
    edges = cv2.erode(temp, np.ones((3,3)), iterations=6)
    edges = cv2.dilate(edges, np.ones((3,3)), iterations=4)

    edges = cv2.erode(temp - edges, np.ones((3,3)), iterations = 5)

    #cv2.imshow('temp', temp)
    #cv2.imshow('edges', edges)

    drawSquare(im, sbig)
    drawSquare(im, ssmall)
    
    region(edges, sbig, ssmall)

    return edges, im
