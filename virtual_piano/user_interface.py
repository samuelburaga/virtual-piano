import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QFileDialog,
    QSizePolicy,
)
from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QIcon, QFont, QPalette


import cv2 as cv
import mediapipe as mp
import math
import threading
import sys

from enum import Enum

MAXIMUM_NUMBER_OF_WEBCAMS_ASSUMED = 10
PRESS_THRESHOLD = 40
PIANO_WHITE_KEY = {"WIDTH": 40, "HEIGHT": 200}
PIANO_BLACK_KEY = {"WIDTH": 20, "HEIGHT": 120}
PIANO_OFFSET = {"X": 100, "Y": 100}
NUMBER_OF_OCTAVES_TO_BE_DRAWN = 2
PRIMARY_COLOR = (64, 54, 251)
PRESSED_KEY_COLOR = PRIMARY_COLOR


class KeyTypeEnum(Enum):
    WHITE_KEY = "WHITE_KEY"
    BLACK_KEY = "BLACK_KEY"


# from constants import *
from utils.piano.ui_utils import *
from utils.piano.sound_utils import start_piano
from utils.recording.video_utils import *
from utils.recording.audio_utils import *
from screeninfo import get_monitors


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
rect_x1, rect_y1 = 100, 100
rect_x2, rect_y2 = 140, 300
hands = mp_hands.Hands()


def get_monitor_information():
    return get_monitors()[0]


class WebcamWindow(QWidget):
    def __init__(self, webcam_stream_widget, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Webcam Feed")
        layout = QVBoxLayout()
        layout.addWidget(webcam_stream_widget.video_label)
        webcam_stream_widget.is_full_screen = True
        self.setLayout(layout)
        self.resize(1920, 1080)  #

    def closeEvent(self, event):
        self.hide()
        event.ignore()


class MainApplicationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Virtual Piano")

        self.title_widget = TitleWidget()
        self.instructions_widget = InstructionsWidget()
        self.options_widget = OptionsWidget()
        self.webcam_stream_widget = WebcamStreamWidget()
        self.quit_button_widget = QuitButtonWidget()
        # self.stepper_widget = StepperWidget()

        # Set the quit callback
        self.options_widget.record_button_widget.on_click_callback(
            self.handle_recording
        )
        self.options_widget.full_screen_widget.on_click_callback(
            self.make_webcam_full_screen
        )
        self.quit_button_widget.on_click_callback(self.close_application)

        # Set up the main layout
        central_widget = QWidget()

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.title_widget)
        main_layout.addWidget(self.instructions_widget)
        # main_layout.addWidget(self.stepper_widget)
        main_layout.addWidget(self.options_widget)
        main_layout.addWidget(self.webcam_stream_widget)
        main_layout.addWidget(self.quit_button_widget)

        central_widget.setLayout(main_layout)

        self.setCentralWidget(central_widget)

    def handle_recording(self):
        background_thread = threading.Thread(target=start_audio_recording)
        background_thread.daemon = True
        background_thread.start()

    def make_webcam_full_screen(self):
        if not hasattr(self, "webcam_window"):
            self.webcam_window = WebcamWindow(self.webcam_stream_widget, self)
            self.webcam_window.show()

    def close_application(self):
        self.webcam_stream_widget.webcam_capture.release()
        self.close()

    def closeEvent(self, event):
        self.webcam_stream_widget.webcam_capture.release()
        event.accept()


class WebcamStreamWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.is_full_screen = False
        # Set up the UI
        self.layout = QVBoxLayout()

        # Add a label to display the webcam feed
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)  # Align the label in the center
        self.layout.addWidget(self.video_label, alignment=Qt.AlignCenter)

        self.setLayout(self.layout)

        # Initialize the webcam
        self.monitor_information = get_monitor_information()
        self.webcam_capture = cv2.VideoCapture(0)
        self.frame_width = int(self.webcam_capture.get(cv.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.webcam_capture.get(cv.CAP_PROP_FRAME_HEIGHT))
        self.webcam_dimensions = (self.frame_width, self.frame_height)

        self.frame_rate = int(self.webcam_capture.get(cv.CAP_PROP_FPS))
        if self.frame_rate > 0:
            self.interval = int(1000 / self.frame_rate)
        else:
            self.interval = 33
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(self.interval)
        self.webcam_capture_position_X = (
            self.monitor_information.width - self.frame_width
        ) // 2
        self.webcam_capture_position_Y = (
            self.monitor_information.height - self.frame_width
        ) // 2
        start_piano()

    def update_frame(self):
        data, frame = self.webcam_capture.read()
        if data:
            frame = cv2.cvtColor(cv.flip(frame, 1), cv.COLOR_RGB2BGR)
            results = hands.process(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

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

            # write_frame(frame)

            # key_pressed = cv.waitKey(1) & 0xFF
            # if key_pressed == ord("q"):
            #     break

            # Convert the frame to RGB format
            if self.is_full_screen is True:
                frame = cv2.resize(
                    frame,
                    (self.monitor_information.width, self.monitor_information.height),
                )
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            step = channel * width
            qimg = QImage(frame.data, width, height, step, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(qimg))


class RecordButtonWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the UI with a button
        layout = QVBoxLayout()
        # Add a button with an icon and label to close the application

        self.record_button = QPushButton("Start recording audio")
        self.record_button.setIcon(
            QIcon("assets/images/svg/record-svgrepo-com.svg")
        )  # Set the icon (ensure 'icon.png' exists in the same directory)
        self.record_button.setIconSize(QSize(24, 24))  # Set the size of the icon
        layout.addWidget(self.record_button, alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def on_click_callback(self, callback):
        self.record_button.clicked.connect(callback)


class QuitButtonWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the UI with a button
        layout = QVBoxLayout()
        # Add a button with an icon and label to close the application

        # Add a button to close the application
        self.quit_button = QPushButton("Quit")
        self.quit_button.setIcon(
            QIcon("assets/images/svg/arrow-right-from-bracket-svgrepo-com.svg")
        )  # Set the icon (ensure 'icon.png' exists in the same directory)
        self.quit_button.setIconSize(QSize(24, 24))  # Set the size of the
        layout.addWidget(self.quit_button, alignment=Qt.AlignRight)
        self.setLayout(layout)

    def on_click_callback(self, callback):
        self.quit_button.clicked.connect(callback)


class FullScreenButtonWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the UI with a button
        layout = QVBoxLayout()
        # Add a button with an icon and label to close the application

        # Add a button to close the application
        self.quit_button = QPushButton("Full screen")
        self.quit_button.setIcon(
            QIcon("assets/images/svg/full-screen-one-svgrepo-com.svg")
        )  # Set the icon (ensure 'icon.png' exists in the same directory)
        self.quit_button.setIconSize(QSize(24, 24))  # Set the size of the
        layout.addWidget(self.quit_button, alignment=Qt.AlignRight)
        self.setLayout(layout)

    def on_click_callback(self, callback):
        self.quit_button.clicked.connect(callback)


class TitleWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        html_text = f"""<h1>Play piano using your webcam!</h1>"""
        self.title = QLabel()
        self.title.setText(html_text)
        self.title.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(24)
        self.title.setFont(font)
        layout.addWidget(self.title)
        self.setLayout(layout)


class InstructionsWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.instructions = QLabel()
        html_text = f"""
        <p style="font-size: 20pt;">
            Instructions: 
        </p>
        <ul style ="font-size: 15pt">
            <li> Place your hands in front the webcam and the algorithm will detect them.</li>
            <li> Bend the tip of your fingers down in order to simulate a key touch. The key will be highlighted and played. </li>
            <li> Chose a path for the audio recording output </li>
            <li> Press the "Start recording" button. </li>
            <li> when you finished, stop the recording. </li>
        </ul>
        """
        self.instructions.setText(html_text)

        self.instructions.setAlignment(Qt.AlignJustify)
        self.instructions.setWordWrap(True)
        font = QFont()
        font.setPointSize(24)
        self.instructions.setFont(font)
        layout.addWidget(self.instructions)
        layout.setContentsMargins(100, 50, 0, 0)
        self.setLayout(layout)


class PathSelectorWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.button = QPushButton("Choose Path", self)
        self.button.setIcon(QIcon("assets/images/svg/file-folder-svgrepo-com (3).svg"))
        self.button.clicked.connect(self.choosePath)
        self.button.setIconSize(QSize(24, 24))  # Set the size of the icon
        layout.addWidget(self.button, alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def choosePath(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        folder_path = QFileDialog.getExistingDirectory(
            self, "Choose Folder", options=options
        )
        if folder_path:
            print("Selected Folder Path:", folder_path)
            # Use the folder_path variable in your code


class OptionsWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        layout.setSpacing(100)
        layout.addStretch(-1)
        layout.setContentsMargins(0, 0, 910, 0)
        self.path_selector_widget = PathSelectorWidget()
        self.record_button_widget = RecordButtonWidget()
        self.full_screen_widget = FullScreenButtonWidget()
        layout.addWidget(self.path_selector_widget)
        layout.addWidget(self.record_button_widget)
        layout.addWidget(self.full_screen_widget)
        self.setLayout(layout)


class Slide(QWidget):
    def __init__(self, label, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        self.instructions = QLabel()
        html_text = f"""
        <p style="font-size: 20pt;">
            {label}
        </p>
        """
        self.instructions.setText(html_text)
        self.instructions.setAlignment(Qt.AlignJustify)
        self.instructions.setWordWrap(True)
        font = QFont()
        font.setPointSize(24)
        self.instructions.setFont(font)
        layout.addWidget(self.instructions)
        self.setLayout(layout)


class StepperWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("PyQt5 Stepper Example")

        self.instructions = QLabel()
        html_text = f"""
        <p style="font-size: 20pt;">
            Instructions: 
        </p>"""

        self.instructions.setText(html_text)

        layout = QVBoxLayout()
        layout.addWidget(self.instructions)
        # Stack to hold slides
        self.stackedWidget = QStackedWidget()

        # Add slides to the stack
        slide1 = Slide(
            "Place your hands in front the webcam and the algorithm will detect them"
        )
        slide2 = Slide(
            "Bend the tip of your fingers down in order to simulate a key touch. The key will be highlighted and played"
        )
        slide3 = Slide("Chose a path for the audio recording output")
        slide4 = Slide('Press the "Start recording" button')
        slide5 = Slide("When you finished, stop the recording")

        self.stackedWidget.addWidget(slide1)
        self.stackedWidget.addWidget(slide2)
        self.stackedWidget.addWidget(slide3)
        self.stackedWidget.addWidget(slide4)
        self.stackedWidget.addWidget(slide5)

        # Navigation buttons
        nextButton = QPushButton("Next")
        nextButton.clicked.connect(self.nextSlide)
        # nextButton.setStyleSheet(
        #     """background-color: red; font-size: 16px; color: white; border-radius: 10px; padding: 10px;"""
        # )
        palette = nextButton.palette()
        palette.setColor(QPalette.Button, Qt.GlobalColor.blue)
        nextButton.setAutoFillBackground(True)
        nextButton.setPalette(palette)
        prevButton = QPushButton("Previous")
        prevButton.clicked.connect(self.prevSlide)

        layout.addWidget(self.stackedWidget)
        layout.addWidget(prevButton)
        layout.addWidget(nextButton)

        self.setLayout(layout)

    def nextSlide(self):
        currentIndex = self.stackedWidget.currentIndex()
        if currentIndex < self.stackedWidget.count() - 1:
            self.stackedWidget.setCurrentIndex(currentIndex + 1)

    def prevSlide(self):
        currentIndex = self.stackedWidget.currentIndex()
        if currentIndex > 0:
            self.stackedWidget.setCurrentIndex(currentIndex - 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApplicationWindow()
    window.showMaximized()  # Show the window maximized
    sys.exit(app.exec_())
