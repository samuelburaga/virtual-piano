import cv2 as cv
from constants.constants import *


are_white_keys_drawn = False
are_black_keys_drawn = False
white_keys_positions = []
black_keys_positions = []


def highlight_pressed_key(frame, tip_point_position):
    key_found = False

    for i in range(len(black_keys_positions)):
        if (
            tip_point_position[0] >= black_keys_positions[i][0][0]
            and tip_point_position[0] <= black_keys_positions[i][1][0]
            and tip_point_position[1] >= black_keys_positions[i][0][1]
            and tip_point_position[1] <= black_keys_positions[i][1][1]
        ):
            key_found = True
            cv.rectangle(
                frame,
                black_keys_positions[i][0],
                black_keys_positions[i][1],
                PRESSED_KEY_COLOR,
                -1,
            )
            break

    if key_found is False:
        for i in range(len(white_keys_positions)):
            if (
                tip_point_position[0] >= white_keys_positions[i][0][0]
                and tip_point_position[0] <= white_keys_positions[i][1][0]
            ):
                cv.rectangle(
                    frame,
                    white_keys_positions[i][0],
                    white_keys_positions[i][1],
                    PRESSED_KEY_COLOR,
                    -1,
                )
                for j in range(NUMBER_OF_OCTAVES_TO_BE_DRAWN):
                    draw_black_keys(frame, 50 + 7 * j * PIANO_WHITE_KEY["WIDTH"])

                break


def draw_black_keys(frame, start_X):
    global are_black_keys_drawn
    for index in range(6):
        if index != 2:  # between E and F
            top_left_corner = (
                start_X
                + index * PIANO_WHITE_KEY["WIDTH"]
                + PIANO_WHITE_KEY["WIDTH"]
                - PIANO_BLACK_KEY["WIDTH"] // 2,
                100,
            )
            bottom_right_corner = (
                start_X
                + index * PIANO_WHITE_KEY["WIDTH"]
                + PIANO_WHITE_KEY["WIDTH"]
                - PIANO_BLACK_KEY["WIDTH"] // 2
                + PIANO_BLACK_KEY["WIDTH"],
                100 + PIANO_BLACK_KEY["HEIGHT"],
            )
            cv.rectangle(
                frame,
                top_left_corner,
                bottom_right_corner,
                (0, 0, 0),
                -1,
            )
            if are_black_keys_drawn is False:
                black_keys_positions.append([top_left_corner, bottom_right_corner])
    if len(black_keys_positions) / 5 == NUMBER_OF_OCTAVES_TO_BE_DRAWN:
        are_black_keys_drawn = True


def draw_white_keys(frame, start_X):
    global are_white_keys_drawn
    for i in range(7):
        top_left_corner = start_X + i * PIANO_WHITE_KEY["WIDTH"], 100
        bottom_right_corner = (
            start_X + (i + 1) * PIANO_WHITE_KEY["WIDTH"],
            100 + PIANO_WHITE_KEY["HEIGHT"],
        )

        cv.rectangle(
            frame,
            top_left_corner,
            bottom_right_corner,
            (255, 255, 255),
            -1,
        )

        cv.rectangle(
            frame,
            top_left_corner,
            bottom_right_corner,
            (0, 0, 0),
            1,
        )
        if are_white_keys_drawn is False:
            white_keys_positions.append([top_left_corner, bottom_right_corner])
    if len(white_keys_positions) / 7 == NUMBER_OF_OCTAVES_TO_BE_DRAWN:
        are_white_keys_drawn = True


def draw_octave(frame, octaveCounter):
    start_X = 50 + 7 * (octaveCounter - 1) * PIANO_WHITE_KEY["WIDTH"]
    draw_white_keys(frame, start_X)
    draw_black_keys(frame, start_X)
