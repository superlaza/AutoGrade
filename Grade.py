#these imports are for debugging
import cv2
from scipy.cluster.vq import kmeans, whiten
import numpy as np

'''The answer map should only be generated once, so we should make this
a class with a variable that stores that result. Right now, i'm calculating
the answer map twice
'''

#squareOrigin = (25, 45)

#using deprecated version. as per the docs notes, returns dict with structure
# {(answer number, letter) : (coordx, coordy)}
def getAnswerMap(im, squareOrigin):
    (ox, oy) = (squareOrigin[0], squareOrigin[1])
    (h, w) = (im.shape[0], im.shape[1]) #first two dimensions w and h
    answerMap = {}

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
            answerMap[(i,j)] = circle_1
            answerMap[(i+17,j)] = circle_2
            circlex+=(0.025882*w)

    return answerMap

#iterate through values instead
def drawAnswerCoords(im):
    answerMap = getAnswerMap(im, (25, 45))
    for answer in answerMap:
        cv2.circle(im, answerMap[answer] , 4, (255,255,255), -1)

def convolve(im, point):
    #radius should not be hardcoded
    radius = 4
    sum = 0
    for i in range(0, 2 * radius):
        for j in range(0, 2 * radius):
            sum += im[point[1] - radius + i][point[0] +- radius + j]
    return sum

def grade(registered):
    #doesn't actually draw circles, returns locations of bubble centers taken from perfect template
    #the ordered pair argument is the offset to the upperleft corner, shouldn't be hardcoded
    answerMap = getAnswerMap(registered, (25, 45))

    #programmatically determine treshold for convolutions
    retval, registered = cv2.threshold(registered, 80, 255, cv2.THRESH_BINARY_INV)
    convs = []
    for pair in answerMap:
        convs.append(convolve(registered, answerMap[pair]))
    out = kmeans(np.array(convs), 2)[0]
    thresh = (max(out.tolist())-min(out.tolist()))/2
    
    #for every bubble coordinate, convolve that location with a kernal to see if that answer was bubbled
    answers = {}
    for pair in answerMap:
        if(convolve(registered, answerMap[pair]) > thresh):
            (num,ans) = pair
            letter = "A"
            if(ans == 0 or ans == 5):
                letter = "A"
            elif(ans == 1 or ans == 6):
                letter = "B"
            elif(ans == 2 or ans == 7):
                letter = "C"
            elif(ans == 3 or ans == 8):
                letter = "D"
            elif(ans == 4 or ans == 9):
                letter = "E"
            answers[num + 1] = letter
    for key in sorted(answers.iterkeys()):
        print "%d: %s" % (key, answers[key])
