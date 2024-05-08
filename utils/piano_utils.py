import cv2 as cv
from constants.constants import *


def draw_black_keys(frame, start_X):
    for index in range(6):
        if index != 2:  # between E and F
            cv.rectangle(
                frame,
                (
                    start_X
                    + index * PIANO_WHITE_KEY["WIDTH"]
                    + PIANO_WHITE_KEY["WIDTH"]
                    - PIANO_BLACK_KEY["WIDTH"] // 2,
                    100,
                ),
                (
                    start_X
                    + index * PIANO_WHITE_KEY["WIDTH"]
                    + PIANO_WHITE_KEY["WIDTH"]
                    - PIANO_BLACK_KEY["WIDTH"] // 2
                    + PIANO_BLACK_KEY["WIDTH"],
                    100 + PIANO_BLACK_KEY["HEIGHT"],
                ),
                (0, 0, 0),
                -1,
            )


def draw_white_keys(frame, start_X):
    for i in range(7):
        cv.rectangle(
            frame,
            (start_X + i * PIANO_WHITE_KEY["WIDTH"], 100),
            (
                start_X + (i + 1) * PIANO_WHITE_KEY["WIDTH"],
                100 + PIANO_WHITE_KEY["HEIGHT"],
            ),
            (255, 255, 255),
            -1,
        )
        cv.rectangle(
            frame,
            (start_X + i * PIANO_WHITE_KEY["WIDTH"], 100),
            (
                start_X + (i + 1) * PIANO_WHITE_KEY["WIDTH"],
                100 + PIANO_WHITE_KEY["HEIGHT"],
            ),
            (0, 0, 0),
            1,
        )


def draw_octave(frame, octaveCounter):
    start_X = 50 + 7 * (octaveCounter - 1) * PIANO_WHITE_KEY["WIDTH"]
    draw_white_keys(frame, start_X)
    draw_black_keys(frame, start_X)
