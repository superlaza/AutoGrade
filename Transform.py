import cv2
import numpy as np
import Errors

def transform(im, points):
    #three points and their mapped versions used to compute underlying affine transform
    dstTriangle = np.array([[25,45],[25,336],[307,45]], np.float32)
    srcTriangle = np.array(points,np.float32)
    
    if (not (len(dstTriangle) - len(srcTriangle)) == 0):
        raise Errors.NotEnoughPointsToTransformError
    
    #compute transform based on point mappings above
    transform = cv2.getAffineTransform(srcTriangle, dstTriangle)

    #get image dimension (redundant), then apply derived transform to obtain registered image
    rows, cols, depth = im.shape
    registered = cv2.warpAffine(im, transform, (cols, rows))
    
    #adjust template to show difference between it and the registered image
    template = cv2.cvtColor(cv2.imread('answerTemplate.jpg'), cv2.COLOR_BGR2GRAY)
    blank = np.ones((2200, 2200), dtype = np.uint8) * 255
    blank[:, :1700] = template
    #template = cv2.resize(blank, (500,500))
    template = cv2.resize(blank, (640, 480))

    print template.shape
    print registered.shape
    registered = cv2.cvtColor(registered, cv2.COLOR_BGR2GRAY)    
    blend = cv2.addWeighted(registered, .7, template, .3, 0)

    return registered, blend
