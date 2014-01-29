def drawCircles(im, squareOrigin):
    (ox, oy) = (squareOrigin[0], squareOrigin[1])
    (h, w) = (im.shape[0], im.shape[1]) #first two dimensions w and h

    bubbles = []

    radius = int(round(4 * (0.009411 * h)))
    rows = 17
    col = 2
    for i in range(0, rows):
        wOffset = 0.070588 * w
        hOffset = 0.07636 * h
        circlex = ox + wOffset
        circley = oy + hOffset + i * (0.02625 * h)
        for j in range(0, 5):
            circle_1 = (int(round(circlex)), int(round(circley)))
            circle_2 = (int(round(circlex + (0.18824 * w))), int(round(circley)))
            #cv2.circle(im, circle_1 , 5, (255,255,255), -1)
            #cv2.circle(im, circle_2 , 5, (255,255,255), -1)
            bubbles += [circle_1, circle_2]
            circlex += (0.025882 * w)

    return bubbles

def convolve(im, point):
    #radius should not be hardcoded
    radius = 4
    sum = 0
    for i in range(0, 2 * radius):
        for j in range(0, 2 * radius):
            sum += im[point[1] - radius + i][point[0] +- radius + j]
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
    
    j = (y - (oy + hOffset)) / (h2 * h)
    if int((x - (ox + wOffset)) / 70) == 0:
        i = (x - (ox + wOffset)) / (w2 * w)
    else:
        i = ((x - (ox + wOffset + 80)) / (w2 * w)) + 5
        j += rows

    return (int(round(j)), int(round(i)))

def grade(registered):
    #cv2.imshow("warped.png",registered)
    #doesn't actually draw circles, returns locations of bubble centers taken from perfect template
    #the ordered pair argument is the offset to the upperleft corner, shouldn't be hardcoded
    bubbles = drawCircles(registered, (29, 49))

    #for every bubble coordinate, convolve that location with a kernal to see if that answer was bubbled
    answers = {}
    '''i should fix threshold for convolution'''
    for pair in bubbles:
        if(convolve(registered, pair) > 7000):
            (num, ans) = findAnswer(registered, (25, 45), pair)
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
            #print "ans: "+str(num+1)+", "+letter
    for key in sorted(answers.iterkeys()):
        print "%d: %s" % (key, answers[key])
