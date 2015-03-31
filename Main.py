import cv2
import numpy as np
from scipy.optimize import minimize
from Preprocess import win, draw_square, preprocess, region, show_intersections
from FindPoints import findPoints
from Transform import transform, myDims
from Grade import grade, ndrawAnswerCoords
import Errors

# debugging
import sys
import traceback
import time

camera_port = 0
ramp_frames = 4

suppress = True

# debugging
debug = \
    {
        'suppress': True
    }

views = \
    {
        'reg': True,
        'corners': False,
        'edges': False,
        'thresh': False,
        'blend': True,
        'visual': False
    }


# to turn on/off views at runtime, view list above is global
def toggle_view(view_name, image):
    if views[view_name]:
        cv2.imshow(view_name, image)
    elif cv2.getWindowProperty(view_name, cv2.CV_WINDOW_AUTOSIZE) > 0:  #  get any window prop to check for existence
        cv2.destroyWindow(view_name)


# makes a function to pass to minimization
def affine_dec(image, template_math):
    rows, cols = image.shape

    def affine(d):
        [dx, dy] = d
        m = np.float32([[1, 0, dx], [0, 1, dy]])
        dst = cv2.warpAffine(image, m, (cols, rows))
        return np.sum(cv2.bitwise_and(dst, template_math))

    return affine


def main():
    # for criterion, minval can be any exorbitantly large value
    minval = 500000000
    quota = 0
    
    camera = cv2.VideoCapture(camera_port)

    for i in xrange(ramp_frames):
        retval, temp = camera.read()


    while True:
        start_time = time.time()
        # The function waitKey waits for a key event infinitely (when delay<=0 )
        # or for delay milliseconds, when it is positive. It returns the code of
        # the pressed key or -1 if no key was pressed before the specified time
        # had elapsed. Escape code is 27
        wk = cv2.cv.WaitKey(10)
        print wk

        # registration criterion, only grade if we've improved 7 times
        # break on space bar
        if quota == 20 or wk == 32:
            # if registered exists, try grading it. otherwise, break
            # if reg exists and you grade it successfully, break. o/w keep going
            if 'registered' in locals():
                try:
                    print 'grading...'
                    if not grade(registered):
                        cv2.imwrite('misaligned.jpg', blend_visual)
                        quota = 0
                    else:  # we stop only when we get a complete grade
                        break
                except:
                    if not suppress:
                        print "something bad is happening at Grade"
            else:
                break

        # escapes
        if wk == 27:  #  escape
            break

        # dynamic views, there's a better structure for this
        if wk == 114:  # r
            views['reg'] = not views['reg']
        if wk == 99:  # c
            views['corners'] = not views['corners']
        if wk == 101:  # e
            views['edges'] = not views['edges']
        if wk == 116:  # t
            views['thresh'] = not views['thresh']
        if wk == 98:  # b
            views['blend'] = not views['blend']
        if wk == 118:  # v
            views['visual'] = not views['visual']

        # output control
        if wk == 115:
            debug['suppress'] = not debug['suppress']

        retval, im = camera.read()

        try:
            im = np.array(im[:, :im.shape[0], :])
            im = cv2.resize(im, win)

            # present feed for input
            draw_square(im)
            cv2.imshow('input', cv2.flip(im, 1))

            gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 240)
            region(edges, margin=0)

            toggle_view('edges', edges)
            
            intersections = findPoints(edges)

        except Errors.ImproperIntersectionsError as e:
            if not suppress:
                print e
            continue
        except Exception as e:
            if not suppress:
                print e, traceback.format_exception(*sys.exc_info())
            continue
        
        # if no points found, this code isn't seen
        # show computed intersection points
        for point in intersections:
            cv2.circle(im, (int(round(point[0])), int(round(point[1]))), 6, (0, 0, 255), -1)
        toggle_view('corners', cv2.flip(im, 1))

        try:
            registered = transform(im, intersections)
            toggle_view('reg', registered)
        except Errors.NotEnoughPointsToTransformError as e:
            if not suppress:
                print e
            continue
        
        # adjust registered
        registered = cv2.cvtColor(registered, cv2.COLOR_BGR2GRAY)
        retval, registered_bin = cv2.threshold(registered, 120, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

        '''==========BLENDING AND REGISTRATION CRITERION=========='''
                    # -----------------------------
                    # This is for visual comparison
                    # -----------------------------
        if views['visual']:
            # template to show difference between it and the registered image
            # this read incurs a 5-fold decrease in speed
            template_visual = cv2.cvtColor(cv2.imread('blank.jpg'), cv2.COLOR_BGR2GRAY)
            # reduce to dimensions to match registered
            template_visual = cv2.resize(template_visual, (0, 0), fx=0.25, fy=0.25)
            blend_visual = cv2.addWeighted(registered, .7, template_visual, .3, 0)
            cv2.imshow('visual blend', blend_visual)
        elif cv2.getWindowProperty('visual blend', cv2.CV_WINDOW_AUTOSIZE) > 0:  #  get any window prop to check for existence
                cv2.destroyWindow('visual blend')
                    # -----------------------------------
                    # This is for mathematical comparison
                    # -----------------------------------
        # create criterion template, reverse size tuple
        template_math = np.zeros(myDims[::-1], dtype=np.uint8)
        template_math = ndrawAnswerCoords(template_math)

        # compute blend
        blend_math = cv2.bitwise_and(registered_bin, template_math)

        # impose criterion
        blend_sum = np.sum(blend_math)
        toggle_view('blend', blend_math)
        if blend_sum < minval:
            # take {quote} improvements before showing grade
            print blend_sum
            quota += 1
            minval = blend_sum

        print "time: ", time.time()-start_time
        '''======================================================='''
        
    cv2.cv.DestroyAllWindows()
    camera.release()

if __name__ == '__main__':
    main()
