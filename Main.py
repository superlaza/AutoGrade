import cv2
import numpy as np
from Preprocess import preprocess
from FindPoints import findPoints
from Transform import transform
from Grade import grade,ndrawAnswerCoords
import Errors

camera_port = 0
ramp_frames = 4

#for debugging
'''opts: output, preprocessed, blend'''
view = "output"
suppress = True

#to draw image with aligned circles to test alignment of regged image

def main():
    #for criterion, minval can be any exorbitantly large value
    minval = 500000000
    quota = 0
    
    camera = cv2.VideoCapture(camera_port)

    for i in xrange(ramp_frames):
        retval, temp = camera.read()

    while True:
        #The function waitKey waits for a key event infinitely (when delay<=0 )
        #or for delay milliseconds, when it is positive. It returns the code of
        #the pressed key or -1 if no key was pressed before the specified time
        #had elapsed. Escape code is 27
        wk = cv2.cv.WaitKey(10)

        #registration criterion, only grade if we've improved 7 times
        #break on space bar
        if quota == 6 or wk == 32:
            #if registered exists, try grading it. otherwise, break
            #if reg exists and you grade it successfully, break. o/w keep going
            if 'registered' in locals():
                grade(registered)
                try:
                    if not grade(registered):
                        cv2.imwrite('misaligned.jpg', blend_visual)
                    break
                except:
                    if not suppress:
                        print "something bad is happening at Grade"
            else:
                break
        
        retval, im = camera.read()
        
        try:
            edges, im = preprocess(im)

            if view == "processed":
                cv2.imshow('edges', edges)
            if view == "output" or view =="region" or view == "blend":
                cv2.imshow("image", cv2.flip(im, 1))
            
            intersections = findPoints(edges)
            
        except Errors.ImproperIntersectionsError as e:
            if not suppress:
                print e
            continue
        except:
            if not suppress:
                print "something bad is happening at preprocess"
            continue
        
        '''
        #show window around points
        w = 30
        for point in intersections:
            cv2.circle(im, (int(round(point[0])), int(round(point[1]))),
                       1, (0,0,255), -1)
            cv2.imwrite(str(point)+'.jpg', cv2.resize(im[point[0]-w:point[0]+w,point[1]-w:point[1]+w], (0,0), fx=4, fy=4))        
        '''
        
        #if no points found, this code isn't seen
        #show computed intersection points
        for point in intersections:
            cv2.circle(im, (int(round(point[0])), int(round(point[1]))),
                       6, (0,0,255), -1)

        if view == "output":
            cv2.imshow("drawn intersections", cv2.flip(im, 1))
        

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
        template_visual = cv2.cvtColor(cv2.imread('blank.jpg'), cv2.COLOR_BGR2GRAY)
        #reduce to 1/4 size
        size = (int(round(0.25*template_visual.shape[1])), int(round(0.25*template_visual.shape[0])))
        template_visual = cv2.resize(template_visual, size)
    
                    #-----------------------------------
                    #This is for mathematical comparison
                    #-----------------------------------
        #create criterion template, reverse size tuple
        template_math = np.zeros(size[::-1], dtype=np.uint8)
        template_math = ndrawAnswerCoords(template_math)
        
        #adjust registered
        registered = cv2.cvtColor(registered, cv2.COLOR_BGR2GRAY)
        retval, registered_bin = cv2.threshold(registered, 120, 255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

        #compute blend
        blend_math = cv2.bitwise_and(registered_bin, template_math)
        blend_visual = cv2.addWeighted(registered, .7, template_visual, .3, 0)

        #impose criterion
        blend_sum = np.sum(blend_math)
        if blend_sum < minval:
            #take 10 improvements before showing grade
            print blend_sum
            quota += 1
            minval = blend_sum

            if view == "output" or view == "blend":
                cv2.imshow("blended", blend_math)
        
        '''======================================================='''
        
    cv2.cv.DestroyAllWindows()
    camera.release()

if __name__ == '__main__':
    main()
