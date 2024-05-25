import mediapipe as mp

from screeninfo import get_monitors


def get_monitor_information():
    return get_monitors()[0]


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
rect_x1, rect_y1 = 100, 100
rect_x2, rect_y2 = 140, 300
hands = mp_hands.Hands()
