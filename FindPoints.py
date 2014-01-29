import cv2
import numpy as np
import math
from scipy.cluster.vq import kmeans, whiten
import Errors

pi = cv2.cv.CV_PI

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

def computeIntersect(line1, line2):
    [l1p1, l1p2] = lineToPointPair(line1)
    [l2p1, l2p2] = lineToPointPair(line2)
    [x1, y1] = l1p1
    [x2, y2] = l1p2
    [x3, y3] = l2p1
    [x4, y4] = l2p2

    denom = (x1 - x2) * (y3-y4) - (y1 - y2) * (x3 - x4)
    intersect = [(((x1 * y2) - (y1 * x2)) * (x3 - x4)
                  - (x1 - x2) * ((x3 * y4) - (y3 * x4))) / denom,
                 (((x1 * y2) - (y1 * x2)) * (y3 - y4)
                  - (y1 - y2) * ((x3 * y4) - (y3 * x4))) / denom]

    return intersect

def acceptLinePair(line1, line2):
    minTheta = (cv2.cv.CV_PI) / 32
    minThetaDiff = 3 * (cv2.cv.CV_PI) / 8
    maxThetaDiff = 5 * (cv2.cv.CV_PI) / 8
    theta1 = line1[1]
    theta2 = line2[1]

    if (theta1 < minTheta):
        theta1 += pi #deals with 0 and 180 ambiguity
    if (theta2 < minTheta):
        theta2 += pi #deals with 0 and 180 ambiguity

    thetaDiff = abs(theta1-theta2)
    return thetaDiff > minThetaDiff and thetaDiff < maxThetaDiff

def drawIntersection(detectedLines, image):
    #compute the intersection from the lines detected...
    intersections = []
    for i in range(0, detectedLines.shape[0]):
        for j in range(i, detectedLines.shape[0]):
            line1 = detectedLines[i]
            line2 = detectedLines[j]
            if(acceptLinePair(line1, line2)):
                intersection = computeIntersect(line1, line2)
                intersections.append(intersection)
                
    #draw intersections on given image   
    if len(intersections) > 0:
        for i in range(0, len(intersections)):
            p_i = (int(round(intersections[i][0])), int(round(intersections[i][1])))
            cv2.circle(image, p_i , 1, (0, 255, 0), 3)
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

def findPoints(edges, im):
    try:
        #flatten list one level
        lines = cv2.HoughLines( edges, 1, cv2.cv.CV_PI/180, 100)[0]
    except TypeError:
        raise Errors.NotEnoughCannyEdgesError

    if len(lines) < 4:
        raise Errors.NotEnoughCannyEdgesError

    lines = kmeans(lines,8)[0]

    width = pi / 8
    lines = np.array([l for l in lines
                      if not ((l[1] > (pi / 4) - width and l[1] < (pi / 4) + width)
                      or (l[1] > (3 * pi / 4) - width and l[1] < (3 * pi / 4) + width))])

    for line in lines:
        p1 = (int(round(lineToPointPair(line)[0][1])), int(round(lineToPointPair(line)[0][1])))
        p2 = (int(round(lineToPointPair(line)[1][0])), int(round(lineToPointPair(line)[1][1])))
        cv2.line(edges, p1, p2, (255,255,255))

    #compute intersections points of the resultant lines,
    # dropping right-most, bottom-most point
    intersections = drawIntersection(lines, im)
    
    if len(intersections) < 4:
        raise Errors.NotEnoughIntersectionsError

    intersections = kmeans(np.array(intersections), 4)[0].tolist()

    if not validateCorners(intersections):
        raise Errors.ImproperIntersectionsError

    return intersections, im
