import cv2
import numpy as np
import Errors

'''template dims hard coded'''
def transform(im, points):
    #four points and their mapped versions used to compute underlying perspective transform
    #listed as TL, TR, BL, BR
    dstSquare = np.array([[25,45],[307,45],[25,336],[307, 336]], np.float32)
    srcSquare = np.array(points,np.float32)
    
    if (not (len(dstSquare) - len(srcSquare)) == 0):
        raise Errors.NotEnoughPointsToTransformError
    
    #compute transform based on point mappings above
    transform = cv2.getPerspectiveTransform(srcSquare, dstSquare)

    #get image dimension (redundant), then apply derived transform to obtain registered image
    rows, cols, depth = im.shape
    registered = cv2.warpPerspective(im, transform, (425, 550))

    return registered
