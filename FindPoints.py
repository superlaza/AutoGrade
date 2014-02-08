import cv2
import numpy as np
import Errors

def validatePoly(edges, polygon):
    #must be comprised of 4 points
    if len(polygon) == 4:
        #polygon is a stupidly nested structure, each point will be numpy array
        points = [p for [p] in polygon]

        #compute center
        center = np.round(sum(points)/4).astype(int)

        #we have our quad if its center is inside a radius of midpage
        r = 40
        offset = np.array([r,r])
        imcenter = np.array(list(edges.shape[::-1]))/2
        if all(center > imcenter-offset) and all(center < imcenter+offset):
            #sort points into TL, TR, BL, BR
            points = sorted([p for p in points if p[1] < center[1]], key = lambda (px,py): px)+\
                     sorted([p for p in points if p[1] > center[1]], key = lambda (px,py): px)
            return points

    return []

def findPoints(edges):
    #find contours in shallow copy of edges, wipe it, then draw the contours on it
    contourimg = edges.copy()
    contours, hierarchy = cv2.findContours(contourimg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contourimg = np.zeros((500,500), dtype=np.uint8)
    cv2.drawContours(contourimg, contours, -1, (255,255,255), thickness = 1)

    #for every contour found, approximate it with a polygon and filter for
    #the desired quadrilateral
    for cnt in contours:
        polygon = cv2.approxPolyDP(cnt,0.01*cv2.arcLength(cnt,True),True)
        points = validatePoly(edges, polygon)
        if points:
            return points
            
    #if you get through the whole list of contours without finding our quad,
    #throw an exception so the loop runs anew
    raise Errors.ImproperIntersectionsError
