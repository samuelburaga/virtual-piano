import cv2 as cv
import mediapipe as mp
import math
import threading
import sys

from constants.constants import *
from utils.piano.ui_utils import *
from utils.piano.sound_utils import start_piano
from utils.recording.video_utils import *
from utils.recording.audio_utils import *
from utils.recording.audio_utils import recording
from screeninfo import get_monitors


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
rect_x1, rect_y1 = 100, 100
rect_x2, rect_y2 = 140, 300
hands = mp_hands.Hands()


def get_monitor_information():
    return get_monitors()[0]


def start(user_webcams_count):
    start_piano()
    monitor_information = get_monitor_information()

    webcam_capture = cv.VideoCapture(0)
    frame_width = int(webcam_capture.get(cv.CAP_PROP_FRAME_WIDTH))
    frame_height = int(webcam_capture.get(cv.CAP_PROP_FRAME_HEIGHT))
    webcam_dimensions = (frame_width, frame_height)

    frame_rate = int(webcam_capture.get(cv.CAP_PROP_FPS))
    webcam_capture_position_X = (monitor_information.width - frame_width) // 2
    webcam_capture_position_Y = (monitor_information.height - frame_width) // 2

    start_video_recording(frame_rate, webcam_dimensions)
    background_thread = threading.Thread(target=start_audio_recording)
    background_thread.daemon = True
    background_thread.start()

    while True:
        data, frame = webcam_capture.read()
        frame = cv.cvtColor(cv.flip(frame, 1), cv.COLOR_RGB2BGR)
        results = hands.process(frame)
        frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)

        for octaveCounter in range(NUMBER_OF_OCTAVES_TO_BE_DRAWN):
            draw_octave(frame, octaveCounter + 1)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(
                        color=PRIMARY_COLOR, thickness=2, circle_radius=2
                    ),
                )

                landmarks = hand_landmarks.landmark

                for finger_info in [(8, 6), (12, 10), (16, 14), (20, 18)]:
                    tip_id, base_id = finger_info
                    tip_point = (
                        int(landmarks[tip_id].x * frame.shape[1]),
                        int(landmarks[tip_id].y * frame.shape[0]),
                    )
                    base_point = (
                        int(landmarks[base_id].x * frame.shape[1]),
                        int(landmarks[base_id].y * frame.shape[0]),
                    )

                    distance = math.sqrt(
                        (tip_point[0] - base_point[0]) ** 2
                        + (tip_point[1] - base_point[1]) ** 2
                    )

                    if distance < PRESS_THRESHOLD:
                        highlight_pressed_key(frame, tip_point)
                    else:
                        set_keys_status_to_not_played()
                    break

        write_frame(frame)

        cv.imshow("Virtual piano", frame)
        cv.moveWindow(
            "Virtual piano", webcam_capture_position_X, webcam_capture_position_Y
        )

        key_pressed = cv.waitKey(1) & 0xFF
        if key_pressed == ord("q"):
            break

    release_video_recording()
    webcam_capture.release()
    cv.destroyAllWindows()
    time.sleep(2)
    sys.exit()
