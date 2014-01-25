import cv2
import math
import numpy as np
from scipy.cluster.vq import kmeans, whiten

#425, 550

video = True
pi = cv2.cv.CV_PI
win = (500,500)

def drawCircles(im, squareOrigin):
    (ox, oy) = (squareOrigin[0], squareOrigin[1])
    (h, w) = (im.shape[0], im.shape[1]) #first two dimensions w and h

    bubbles = []

    radius = int(round(4*(0.009411*h)))
    rows = 17
    col = 2
    for i in range(0,rows):
        wOffset = 0.070588*w
        hOffset = 0.07636*h
        circlex = ox+wOffset
        circley = oy+hOffset+i*(0.02625*h)
        for j in range(0,5):
            circle_1 = (int(round(circlex)), int(round(circley)))
            circle_2 = (int(round(circlex+(0.18824*w))), int(round(circley)))
            #cv2.circle(im, circle_1 , 5, (255,255,255), -1)
            #cv2.circle(im, circle_2 , 5, (255,255,255), -1)
            bubbles+=[circle_1,circle_2]
            circlex+=(0.025882*w)

    return bubbles

def convolve(im, point):
    #radius should not be hardcoded
    radius = 4
    sum = 0
    for i in range(0,2*radius):
        for j in range(0,2*radius):
            sum+=im[point[1]-radius+i][point[0]+-radius+j]
    return sum

def offset():
    w = 0.070588 / 425 * win[1]
    h = 0.07636 / 550 * win[0]
    h2 = 0.02625 / 550  * win[0]
    w2 = 0.025882 / 425 * win[1]
    return (w,h, h2, w2)

def findAnswer(im, squareOrigin, (x,y)):
    #given a pair of coordinates (x,y), finds (question number, letter answered)
    (ox, oy) = (squareOrigin[0], squareOrigin[1])
    (h, w) = im.shape
    wOffset, hOffset, h2, w2 = offset()
    wOffset *= w
    hOffset *= h

    rows = 17
    col = 2
    
    j = (y - (oy+hOffset))/(h2*h)
    if int((x-(ox+wOffset))/70) == 0:
        i = (x-(ox+wOffset))/(w2*w)
    else:
        i = ((x-(ox+wOffset+80))/(w2*w))+5
        j+=rows

    return (int(round(j)),int(round(i)))
    
def acceptLinePair(line1, line2):
    minTheta = (cv2.cv.CV_PI)/32
    minThetaDiff = 3*(cv2.cv.CV_PI)/8
    maxThetaDiff = 5*(cv2.cv.CV_PI)/8
    theta1 = line1[1]
    theta2 = line2[1]

    if (theta1 < minTheta):
        theta1 += cv2.cv.CV_PI #deals with 0 and 180 ambiguity
    if (theta2 < minTheta):
        theta2 += cv2.cv.CV_PI #deals with 0 and 180 ambiguity

    thetaDiff = abs(theta1-theta2)
    return thetaDiff > minThetaDiff and thetaDiff < maxThetaDiff

def computeIntersect(line1, line2):
    [l1p1, l1p2] = lineToPointPair(line1)
    [l2p1, l2p2] = lineToPointPair(line2)
    [x1,y1] = l1p1
    [x2,y2] = l1p2
    [x3,y3] = l2p1
    [x4,y4] = l2p2

    denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    intersect = [((x1*y2-y1*x2)*(x3-x4)
               -(x1-x2)*(x3*y4-y3*x4))/denom,
               ((x1*y2-y1*x2)*(y3-y4)
                -(y1-y2)*(x3*y4-y3*x4))/denom]

    return intersect

def lineToPointPair(line):

    r = line[0]
    t = line[1]
    cost = math.cos(t)
    sint = math.sin(t)
    x0 = r*cost
    y0 = r*sint
    alpha = 1000

    points = []
    
    points.append([x0+alpha*(-sint), y0+alpha*cost])
    points.append([x0-alpha*(-sint), y0-alpha*cost])

    return points

def drawIntersection(detectedLines, image):
    #compute the intersection from the lines detected...
        intersections = []
        for i in range(0,detectedLines.shape[0]):
            for j in range(i,detectedLines.shape[0]):
                line1 = detectedLines[i]
                line2 = detectedLines[j]
                if(acceptLinePair(line1, line2)):
                    intersection = computeIntersect(line1,line2)
                    intersections.append(intersection)
        #draw intersections on given image   
        if len(intersections)>0:
            for i in range(0,len(intersections)):
                p_i = (int(round(intersections[i][0])),int(round(intersections[i][1])))
                cv2.circle(image, p_i , 1, (0,255,0), 3)
        return intersections

#ideas: compute the center mass from the points and then we can separate the points
    #by those that are above and below then by left and right. if we don't have 4 separate
    # points then it failed. if we do then we have to check further. (how?)
def validateCorners(points):
    '''
    for p in points:
        print p
    pmin = min(points, key = lambda (a,b): a + b)
    pmax = max(points, key = lambda (a,b): a + b)
    points = [p for p in points if not (p == pmin or p == pmax)]
    dist_min1 = math.hypot(points[0][0] - pmin[0], points[0][1] - pmin[1])
    dist_min2 = math.hypot(points[1][0] - pmin[0], points[1][1] - pmin[1])
    dist_max1 = math.hypot(points[0][0] - pmax[0], points[0][1] - pmax[1])
    dist_max2 = math.hypot(points[1][0] - pmax[0], points[1][1] - pmax[1])
    ''''''
    dist1 = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
    dist2 = math.hypot(p3[0] - p1[0], p3[1] - p1[1])
    dist3 = math.hypot(p4[0] - p1[0], p4[1] - p1[1])
    longest = max([dist1, dist2, dist3])
    ''''''
    print pmin
    print pmax
    '''
    return True

#==================================
#==================================
'''NEXT STEPS'''
# 1. restrict attention to the ROI within the white paper (this should be easy)
# 2. figure out the issue behind FLAG1

#==================================
#==================================

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

def process(im):
    sbig = ((80,80), (420,420))
    ssmall = ((150,150), (350,350))
    temp = im
    im = np.array(im[:,:im.shape[0],:])
    im = cv2.resize(im, win)
    gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    reval, thresh = cv2.threshold(gray, 200.0, 255.0, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    
    drawSquare(im, sbig)
    drawSquare(im, ssmall)

    #edges = cv2.Canny(thresh, 100.0, 240.0,2)    
    edges = cv2.Canny(gray, 100.0, 240.0)

    #cv2.imshow('dfd', gedges)
    #cv2.imshow('dfdf', edges)

    #thresh = cv2.GaussianBlur(thresh, (7, 7), 2.0, 2.0)
    blur = thresh

    #edges = cv2.dilate(edges, np.ones((4,4)),iterations=1)

    region(edges, sbig, ssmall)
    cv2.imshow("im", edges)
    #FLAG1: currently not detecting lines close 0 degrees    
    try:
        lines = cv2.HoughLines( edges, 1, cv2.cv.CV_PI/180, 100)[0] #flatten list one level
    except TypeError:
        print "Not enough edges detected by canny"
        if video == True:
            return
    
    if len(lines) < 4:
        return
    print "Detected "+str(lines.shape[0])+" lines"
    #lines = whiten(lines)
    lines = kmeans(lines,8)[0]
    width = pi / 8
    lines = np.array([l for l in lines
                      if not ((l[1] > (pi / 4) - width and l[1] < (pi / 4) + width)
                      or (l[1] > (3 * pi / 4) - width and l[1] < (3 * pi / 4) + width))])
    
    for line in lines:
        p1 = (int(round(lineToPointPair(line)[0][0])),int(round(lineToPointPair(line)[0][1])))
        p2 = (int(round(lineToPointPair(line)[1][0])),int(round(lineToPointPair(line)[1][1])))
        cv2.line(edges, p1, p2, (255,255,255))

    #compute intersections points of the resultant lines, dropping right-most, bottom-most point
    intersections = drawIntersection(lines, im)
    if len(intersections) < 4:
        return
    #intersections = whiten(np.array(intersections))
    intersections = kmeans(np.array(intersections), 4)[0].tolist()

    if not validateCorners(intersections):
        return
    
    #cv2.imshow('image', blur)
    #cv2.imshow('thresh', thresh)
       
    if (video == True and len(intersections)==0):
        print 0
        return

    #show computed intersection points
    try:
        for point in intersections:
            cv2.circle(im, (int(round(point[0])),int(round(point[1]))) , 6, (0,0,255), -1)
    except OverflowError:
        return
    
    cv2.imshow('dfdf', im)
    
    intersections.sort()
    intersections.pop()

    #cv2.imshow('image', im)
    
    #three points and their mapped versions used to compute underlying affine transform
    dstTriangle = np.array([[25,45],[25,336],[307,45]], np.float32)
    srcTriangle = np.array(intersections,np.float32)
    
    if(video == True and not (len(dstTriangle)-len(srcTriangle))==0):
        return
    
    #compute transform based on point mappings above
    transform = cv2.getAffineTransform(srcTriangle,dstTriangle)

    #get image dimension (redundant), then apply derived transform to obtain registered image
    rows,cols,depth = im.shape
    registered = cv2.warpAffine(thresh, transform, (cols,rows))

    template = cv2.cvtColor(cv2.imread('answerTemplate.jpg'),cv2.COLOR_BGR2GRAY)
    blank = np.ones((2200, 2200), dtype=np.uint8) * 255
    blank[:,:1700] = template
    template = cv2.resize(blank, (500,500))
    
    blend = cv2.addWeighted(registered, .7, template, .3, 0)
    cv2.imshow("blend", blend)

    #cv2.imshow("warped.png",registered)
    #doesn't actually draw circles, returns locations of bubble centers taken from perfect template
    #the ordered pair argument is the offset to the upperleft corner, shouldn't be hardcoded
    bubbles = drawCircles(registered, (29,49))
    
    '''need this for still somehow
    if cv2.cv.WaitKey(0) == 27:
        cv2.cv.DestroyAllWindows()
    '''

    #print convolve(registered, bubbles[2])
    
    #for every bubble coordinate, convolve that location with a kernal to see if that answer was bubbled
    answers = {}
    '''i should fix threshold for convolution'''
    for pair in bubbles:
        if(convolve(registered, pair)>7000):
            (num, ans)=findAnswer(registered, (25,45), pair)
            letter = "A"
            if(ans==0 or ans==5):
                letter = "A"
            elif(ans==1 or ans==6):
                letter = "B"
            elif(ans==2 or ans==7):
                letter = "C"
            elif(ans==3 or ans==8):
                letter = "D"
            elif(ans==4 or ans==9):
                letter = "E"
            answers[num+1]=letter
            #print "ans: "+str(num+1)+", "+letter
    for key in sorted(answers.iterkeys()):
        print "%d: %s" %(key, answers[key])
    
if video == False:
    #currently resizing images to match template, this could account for slight errors
    im = cv2.imread("answersPedro.jpg")
    process(im)

    if cv2.cv.WaitKey(0) == 27:
        cv2.cv.DestroyAllWindows()
else:
    camera_port = 0
    ramp_frames = 4
    camera = cv2.VideoCapture(camera_port)
    def get_image():
        retval, im = camera.read()
        return im

    for i in xrange(ramp_frames):
        temp = get_image()
        print temp.shape

    while True:
        im = get_image()
        process(im)
        if cv2.cv.WaitKey(10) == 27:
            break
    cv2.cv.DestroyAllWindows()
