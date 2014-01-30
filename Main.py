import cv2
from Preprocess import preprocess
from FindPoints import findPoints
from Transform import transform
from Grade import grade
import Errors

camera_port = 0
ramp_frames = 4
win = (500,500)
sbig = ((80,80), (420,420))
ssmall = ((150,150), (350,350))

#for debugging
'''opts: output, canny, blend'''
view = "blend"
suppress = False

def get_image(camera):
    retval, im = camera.read()
    return im

def main():
    camera = cv2.VideoCapture(camera_port)

    for i in xrange(ramp_frames):
        temp = get_image(camera)

    while True:
        if cv2.cv.WaitKey(10) == 27:
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
            registered, blend = transform(im, intersections)
        except Errors.NotEnoughPointsToTransformError as e:
            if not suppress:
                print e
            continue

        if view == "output" or view == "blend":
            cv2.imshow("blended", blend)
        
        try:
            grade(registered)
        except:
            if not suppress:
                print "something bad is happening at Grade"
            continue

        #as soon as we grade it once, stop
        #break
        
    cv2.cv.DestroyAllWindows()

if __name__ == '__main__':
    main()
