import cv2
import numpy as np
from AnswerLayout import answerMap, pageDims

#IMPORTANT. radius should be adjusted programmatically, not manually
radius = 10

def ndrawAnswerCoords(im):
    #shape is given as height by width, so it needs to be reversed
    imDims = np.array(list(im.shape[::-1]))
    for num in answerMap:
        for letter in answerMap[num]:
            loc = tuple(np.round(imDims*answerMap[num][letter]).astype(int))
            cv2.circle(im, loc , radius/2, (255,255,255), -1)
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

    #generate local answerMap
    local_answerMap = {}
    for num in answerMap:
        for letter in answerMap[num]:
            loc = tuple(np.round(imDims*answerMap[num][letter]).astype(int))
            if not num in local_answerMap.keys():
                local_answerMap[num] = {}
            local_answerMap[num][letter] = loc
        
    #thresholding
    retval, registered = cv2.threshold(registered, 80, 255, cv2.THRESH_BINARY_INV)


    #there is actually a perfect morphological opening based on circle radius
    #that would remove noise
    registered = cv2.erode(registered, np.ones((3,3)), iterations=6)
    registered = cv2.dilate(registered, np.ones((3,3)), iterations=6)

    #for every number, check which letter has highest convolution
    answers = {}
    for num in local_answerMap:
        max = 0
        for letter in local_answerMap[num]:
            res = convolve(registered, local_answerMap[num][letter])
            if res>max:
                max = res
                answers[num] = letter

    #print answers and check if any were missing
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

    #if numbers are missing, print the registered image
    if len(missing)==0:
        print "complete grade"
        return True
    else:
        print "missing: ", missing
        return False
