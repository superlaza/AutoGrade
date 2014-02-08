import cv2
import numpy as np
import Errors
from AnswerLayout import container, pageDims

'''template dims hard coded'''
#pageDims are (width, height)
myDims = [530,750]

def transform(im, points):
    #four points and their mapped versions used to compute underlying perspective transform
    #lexicographically ordered list
    pList = [np.round((myDims * p)/pageDims).astype(int).tolist() for p in container.pList]

    #error if points are float32
    dstSquare = np.array(pList, np.float32)
    srcSquare = np.array(points,np.float32)
    
    if (not (len(dstSquare) - len(srcSquare)) == 0):
        raise Errors.NotEnoughPointsToTransformError
    
    #compute transform based on point mappings above
    transform = cv2.getPerspectiveTransform(srcSquare, dstSquare)

    registered = cv2.warpPerspective(im, transform, tuple(myDims))

    return registered
