import cv2
import numpy as np
from Preprocess import preprocess
from FindPoints import findPoints
from Transform import transform
from Grade import grade,drawAnswerCoords
import Errors

camera_port = 0
ramp_frames = 4
win = (500,500)
sbig = ((80,80), (420,420))
ssmall = ((150,150), (350,350))

#for debugging
'''opts: output, canny, blend'''
view = "output"
suppress = True

def get_image(camera):
    retval, im = camera.read()
    return im

#to draw image with aligned circles to test alignment of regged image

def main():

    #for criterion
    #minval can be any exorbitantly large value
    minval = 5000000
    quota = 0

    
    camera = cv2.VideoCapture(camera_port)

    for i in xrange(ramp_frames):
        temp = get_image(camera)

    while True:
        if cv2.cv.WaitKey(10) == 27:
            #if escaped, last ditch grade
            grade(registered)
            break
        im = get_image(camera)

        try:
            edges, im = preprocess(im, win, sbig, ssmall)
        except:
            if not suppress:
                print "something bad is happening at preprocess"
            continue

        if view == "canny":
            cv2.imshow('edges', edges)

        if view == "output" or view =="region" or view == "blend":
            cv2.imshow("image", im)
            cv2.imshow("edges", edges)

        try:
            intersections, im = findPoints(edges, im)
        except Errors.NotEnoughCannyEdgesError as e:
            if not suppress:
                print e
            continue
        except Errors.NotEnoughIntersectionsError as e:
            if not suppress:
                print e
            continue
        except Errors.ImproperIntersectionsError as e:
            if not suppress:
                print e
            continue

        #show computed intersection points
        try:
            for point in intersections:
                cv2.circle(im, (int(round(point[0])), int(round(point[1]))),
                           6, (0,0,255), -1)
        except OverflowError as e:
            if not suppress:
                print e
            continue

        if view == "output":
            cv2.imshow("drawn intersections", im)
        
        try:
            registered = transform(im, intersections)
        except Errors.NotEnoughPointsToTransformError as e:
            if not suppress:
                print e
            continue

        '''==========BLENDING AND REGISTRATION CRITERION=========='''
                    #-----------------------------
                    #This is for visual comparison
                    #-----------------------------
        #template to show difference between it and the registered image
        template_visual = cv2.cvtColor(cv2.imread('answerTemplate.jpg'), cv2.COLOR_BGR2GRAY)
        #reduce to 1/4 size
        size = (int(round(0.25*template_visual.shape[1])), int(round(0.25*template_visual.shape[0])))
        template_visual = cv2.resize(template_visual, size)

                    #-----------------------------------
                    #This is for mathematical comparison
                    #-----------------------------------
        #create criterion template, reverse size tuple
        template_math = np.zeros(size[::-1], dtype=np.uint8)
        drawAnswerCoords(template_math)

        #adjust registered
        registered = cv2.cvtColor(registered, cv2.COLOR_BGR2GRAY)
        retval, registered = cv2.threshold(registered, 70, 255, cv2.THRESH_BINARY)

        #compute blend
        blend_math = cv2.bitwise_and(registered, template_math)
        blend_visual = cv2.addWeighted(registered, .7, template_visual, .3, 0)

        #impose criterion
        blend_sum = np.sum(blend_math)
        if blend_sum < minval:
            #take 10 improvements before showing grade
            print blend_sum
            quota += 1
            minval = blend_sum
        else:
            continue
        
        
        if view == "output" or view == "blend":
            cv2.imshow("blended", blend_math)

        '''======================================================='''

        #registration criterion, only grade if we've improved 5 times
        if quota == 4:
            try:
                grade(registered)
            except:
                if not suppress:
                    print "something bad is happening at Grade"
                continue
            break
        
    cv2.cv.DestroyAllWindows()

if __name__ == '__main__':
    main()
