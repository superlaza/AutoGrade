import cv2
import numpy as np

big = ((80,80), (420,420))
small = ((150,150), (350,350))

win = (500, 500)
r_big = 180
# division between integers produces integer (by rounding)
big = (((win[0]/2)-r_big, (win[1]/2)-r_big), ((win[0]/2)+r_big, (win[1]/2)+r_big))


def draw_square(im):
    ((xo, yo), (x, y)) = big
    cv2.line(im, (xo,yo), (x,yo), (0,255,0))
    cv2.line(im, (x,yo), (x,y), (0,255,0))
    cv2.line(im, (x,y), (xo,y), (0,255,0))
    cv2.line(im, (xo,y), (xo,yo), (0,255,0))


def region(im, margin):
    im[:big[0][0]-margin, :] = 0 #top
    im[:, :big[0][1]-margin] = 0 #left
    im[big[1][0]+margin:im.shape[1], :] = 0 #bottom
    im[:, big[1][1]+margin:im.shape[0]] = 0 #right


def show_intersections(im, intersections):
    for point in intersections:
        cv2.circle(im, (int(round(point[0])), int(round(point[1]))),
                   6, (0, 0, 255), -1)
    cv2.imshow("corners", im)


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
