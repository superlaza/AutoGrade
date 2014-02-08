#these imports are for debugging
import cv2
from scipy.cluster.vq import kmeans
import numpy as np
from AnswerLayout import answerMap, pageDims, questions

#IMPORTANT. radius should be adjusted programmatically, not manually
radius = 6

def ndrawAnswerCoords(im):
    #shape is given as height by width, so it needs to be reversed
    imDims = np.array(list(im.shape[::-1]))
    for pair in answerMap:
        loc = tuple(np.round(imDims*answerMap[pair]).astype(int))
        cv2.circle(im, loc , radius, (255,255,255), -1)
    return im
    
def convolve(im, point):
    sum = 0
    for i in range(0, 2 * radius):
        for j in range(0, 2 * radius):
            sum += im[point[1] - radius + i][point[0] - radius + j]
    return sum

'''the registered image is mutated'''
def grade(registered):
    
    #adjust image to match the coords from answerMap
    tempSize = registered.shape
    registered = cv2.resize(registered, tuple(pageDims[::-1]))
    imDims = np.array(list(registered.shape[::-1]))

    #enhance bubbles to ensure they're catched by convolution
    registered = cv2.dilate(registered, np.ones((3,3)), iterations=6)

    local_answerMap = {}
    for pair in answerMap:
        loc = tuple(np.round(imDims*answerMap[pair]).astype(int))
        local_answerMap[pair] = loc
        
    #should programmatically determine treshold for convolutions
    retval, registered = cv2.threshold(registered, 80, 255, cv2.THRESH_BINARY_INV)

    #determine threshold for convolutions
    convs = []
    for pair in local_answerMap:
        convs.append(convolve(registered, local_answerMap[pair]))
    out = kmeans(np.array(convs), 2)[0]
    thresh = (max(out.tolist())-min(out.tolist()))/2

    #for every bubble coordinate, convolve that location with a kernal to see if that answer was bubbled
    answers = {}
    for pair in local_answerMap:
        if(convolve(registered, local_answerMap[pair]) > thresh):
            (num, letter) = pair
            answers[num] = letter
    count = 0
    missing = []
    for num in sorted(answers.iterkeys()):
        print "%d: %c" % (num, answers[num])
        if not count == num:
            missing.append(count)
            count += 1
            while not count == num:
                missing.append(count)
                count += 1
            count += 1
        else:
            count += 1

    #not sure why this is being resized here
    registered = cv2.resize(registered, tempSize[::-1])
    
    if len(missing)==0:
        print "complete grade"
        return True
    else:
        print "missing: ", missing
        #cv2.imwrite('misaligned.jpg', registered)
        return False
