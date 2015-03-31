import cv2
import numpy as np
import Errors
from AnswerLayout import container, pageDims

'''template dims hard coded'''
# pageDims are (width, height)
myDims = [530, 750]


def transform(im, points):
    # four points and their mapped versions used to compute underlying perspective transform
    # lexicographically ordered list
    p_list = [np.round((myDims * p)/pageDims).astype(int).tolist() for p in container.p_list]

    # error if points are float32
    dst_square = np.array(p_list, np.float32)
    src_square = np.array(points, np.float32)
    
    if not (len(dst_square) - len(src_square)) == 0:
        raise Errors.NotEnoughPointsToTransformError
    
    # compute transform based on point mappings above
    _transform = cv2.getPerspectiveTransform(src_square, dst_square)

    registered = cv2.warpPerspective(im, _transform, tuple(myDims))

    return registered
