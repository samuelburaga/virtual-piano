import cv2 as cv

from constants.constants import *


def detect_number_of_webcams():
    webcams_count = 0
    for i in range(MAXIMUM_NUMBER_OF_WEBCAMS_ASSUMED):
        current_webcam_capture = cv.VideoCapture(i)
        if not current_webcam_capture.isOpened():
            break
        webcams_count += 1
        current_webcam_capture.release()
    return webcams_count
