import sys
import cv2 as cv
import threading
from datetime import datetime

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QMainWindow,
    QFileDialog,
)
from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QImage, QPixmap, QIcon, QFont


from constants import *
from constants import PRESS_THRESHOLD, NUMBER_OF_OCTAVES_TO_BE_DRAWN, PRIMARY_COLOR
from piano_ui import *
from piano_sound import start_piano
import piano_sound
from audio_recording import *
from audio_recording import *
from video_recording import *
from opencv_utils import *
from system_utils import *

audio_recording_thread = {}


class WebcamStreamInFullScreenModeWindow(QWidget):
    def __init__(self, webcam_stream_widget, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Virtual piano")

        layout = QVBoxLayout()
        layout.addWidget(webcam_stream_widget.stream_label)
        self.setLayout(layout)

        webcam_stream_widget.is_full_screen = True

        self.resize(
            webcam_stream_widget.monitor_information.width,
            webcam_stream_widget.monitor_information.height,
        )


class MainApplicationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Virtual Piano")

        self.title_widget = TitleWidget()
        self.instructions_widget = InstructionsWidget()
        self.options_widget = OptionsWidget()
        self.webcam_stream_widget = WebcamStreamWidget()
        self.quit_button_widget = QuitButtonWidget()

        self.options_widget.record_button_widget.on_click_callback(
            self.start_audio_recording
        )
        self.options_widget.full_screen_button_widget.on_click_callback(
            self.make_webcam_full_screen
        )
        self.quit_button_widget.on_click_callback(self.close_application)

        widget = QWidget()

        layout = QVBoxLayout()
        layout.addWidget(self.title_widget)
        layout.addWidget(self.instructions_widget)
        layout.addWidget(self.options_widget)
        layout.addWidget(self.webcam_stream_widget)
        layout.addWidget(self.quit_button_widget)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def start_audio_recording(self):
        global audio_recording_thread
        if get_recording_status() is False:
            self.options_widget.path_selector_widget.path_selector_button.setEnabled(
                False
            )
            change_recording_status()
            audio_recording_thread = threading.Thread(target=start_audio_recording)
            audio_recording_thread.daemon = True
            audio_recording_thread.start()

            self.options_widget.record_button_widget.record_button.setText(
                "Recording..."
            )

        else:
            change_recording_status()

            audio_recording_thread.join()
            self.options_widget.record_button_widget.record_button.setText(
                "Start recording"
            )

            self.options_widget.path_selector_widget.path_selector_button.setEnabled(
                True
            )

            open_folder(get_output_path())

    def make_webcam_full_screen(self):
        self.webcam_stream_in_full_screen_mode_window = (
            WebcamStreamInFullScreenModeWindow(self.webcam_stream_widget, self)
        )
        self.webcam_stream_in_full_screen_mode_window.show()

    def close_application(self):
        self.webcam_stream_widget.webcam_capture.release()
        self.close()
        sys.exit

    def closeEvent(self, event):
        self.webcam_stream_widget.webcam_capture.release()
        event.accept()


class TitleWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        text_in_HTML_format = f"""<h1>Play piano using your webcam!</h1>"""
        self.title = QLabel()
        self.title.setText(text_in_HTML_format)
        self.title.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(25)
        self.title.setFont(font)

        layout.addWidget(self.title)
        self.setLayout(layout)


class InstructionsWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.instructions = QLabel()
        text_in_HTML_format = f"""
        <p style="font-size: 20pt;">
            Instructions: 
        </p>
        <ol style ="font-size: 15pt">
            <li>Place your hands in front the webcam and the algorithm will detect them.</li>
            <li>Bend the tip of your fingers down in order to simulate a key touch.</li>
            <li>Chose a path for the audio recording output</li>
            <li>Press the "Start recording" button.</li>
            <li>When you're done playing, stop recording.</li>
            <li>The output folder will be opened automatically.</li>
        </ol>
        """
        self.instructions.setText(text_in_HTML_format)
        self.instructions.setAlignment(Qt.AlignJustify)
        self.instructions.setWordWrap(True)
        font = QFont()
        font.setPointSize(25)
        self.instructions.setFont(font)

        layout.addWidget(self.instructions)
        layout.setContentsMargins(100, 40, 100, 0)
        self.setLayout(layout)


class WebcamStreamWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.is_full_screen = False
        self.layout = QVBoxLayout()

        self.stream_label = QLabel(self)
        self.stream_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.stream_label, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)

        self.webcam_capture = cv.VideoCapture(0)
        start_piano()

        self.frame_width = int(self.webcam_capture.get(cv.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.webcam_capture.get(cv.CAP_PROP_FRAME_HEIGHT))
        self.webcam_dimensions = (self.frame_width, self.frame_height)

        self.frame_rate = int(self.webcam_capture.get(cv.CAP_PROP_FPS))
        if self.frame_rate > 0:
            self.synchronization_time_interval = int(1000 / self.frame_rate)
        else:
            self.synchronization_time_interval = 33

        self.monitor_information = get_monitor_information()
        self.webcam_capture_position_X = (
            self.monitor_information.width - self.frame_width
        )
        self.webcam_capture_position_Y = (
            self.monitor_information.height - self.frame_width
        ) // 2

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_embedded_stream)
        self.timer.start(self.synchronization_time_interval)

    def update_embedded_stream(self):
        data, frame = self.webcam_capture.read()
        if data:
            frame = cv.cvtColor(cv.flip(frame, 1), cv.COLOR_RGB2BGR)
            hands_processing_result = hands.process(frame)
            frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)

            for octaveCounter in range(NUMBER_OF_OCTAVES_TO_BE_DRAWN):
                draw_octave(frame, octaveCounter + 1)

            if hands_processing_result.multi_hand_landmarks:
                for hand_landmarks in hands_processing_result.multi_hand_landmarks:
                    all_landmarks = hand_landmarks.landmark

                    for finger_points_pair in [
                        (4, 3),
                        (8, 7),
                        (12, 11),
                        (16, 15),
                        (20, 19),
                    ]:
                        finger_top_code, second_landmark_code = finger_points_pair

                        finger_top_point = (
                            int(all_landmarks[finger_top_code].x * frame.shape[1]),
                            int(all_landmarks[finger_top_code].y * frame.shape[0]),
                        )

                        second_point = (
                            int(all_landmarks[second_landmark_code].x * frame.shape[1]),
                            int(all_landmarks[second_landmark_code].y * frame.shape[0]),
                        )

                        if is_key_pressed(finger_top_point, second_point):
                            play_pressed_key(frame, finger_top_point)
                        else:
                            piano_sound.WHITE_KEY_WAS_RELEASED[
                                piano_sound.last_white_key_played
                            ] = True
                            piano_sound.BLACK_KEY_WAS_RELEASED[
                                piano_sound.last_black_key_played
                            ] = True

                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS,
                        mp_drawing.DrawingSpec(
                            color=PRIMARY_COLOR, thickness=2, circle_radius=2
                        ),
                    )

            if self.is_full_screen is True:
                frame = cv.resize(
                    frame,
                    (self.monitor_information.width, self.monitor_information.height),
                )
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            h, w, c = frame.shape
            imageFromFrame = QImage(
                frame.data,
                w,
                h,
                c * w,
                QImage.Format_RGB888,
            )
            self.stream_label.setPixmap(QPixmap.fromImage(imageFromFrame))


class OptionsWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()

        self.path_selector_widget = PathSelectorWidget()
        self.record_button_widget = RecordButtonWidget()
        self.full_screen_button_widget = FullScreenButtonWidget()

        layout.addWidget(self.path_selector_widget)
        layout.addWidget(self.record_button_widget)
        layout.addWidget(self.full_screen_button_widget)
        self.setLayout(layout)


class RecordButtonWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.record_button = QPushButton("Start recording")
        self.record_button.setIcon(QIcon("assets/images/svg/record.svg"))
        self.record_button.setIconSize(QSize(25, 25))
        self.record_button.setCursor(Qt.CursorShape.PointingHandCursor)

        layout.addWidget(self.record_button, alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def on_click_callback(self, callback):
        self.record_button.clicked.connect(callback)


class FullScreenButtonWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.full_screen_button = QPushButton("Full screen")
        self.full_screen_button.setIcon(QIcon("assets/images/svg/full-screen.svg"))
        self.full_screen_button.setIconSize(QSize(25, 25))
        self.full_screen_button.setCursor(Qt.CursorShape.PointingHandCursor)

        layout.addWidget(self.full_screen_button, alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def on_click_callback(self, callback):
        self.full_screen_button.clicked.connect(callback)


class QuitButtonWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.quit_button = QPushButton("Quit")
        self.quit_button.setIcon(QIcon("assets/images/svg/exit.svg"))
        self.quit_button.setIconSize(QSize(25, 25))
        self.quit_button.setCursor(Qt.CursorShape.PointingHandCursor)

        layout.addWidget(self.quit_button, alignment=Qt.AlignRight)
        self.setLayout(layout)

    def on_click_callback(self, callback):
        self.quit_button.clicked.connect(callback)


class PathSelectorWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        self.path_selector_button = QPushButton(
            "Choose the output path for the audio file", self
        )
        self.path_selector_button.setIcon(QIcon("assets/images/svg/browse-folder.svg"))
        self.path_selector_button.clicked.connect(self.handleAudioFilePathSelected)
        self.path_selector_button.setIconSize(QSize(25, 25))
        self.path_selector_button.setCursor(Qt.CursorShape.PointingHandCursor)

        text_in_HTML_format = (
            f"""<p>Current output path: {DEFAULT_OUTPUT_ROOT_PATH}</p>"""
        )
        self.current_output_path_label = QLabel()
        self.current_output_path_label.setText(text_in_HTML_format)
        self.current_output_path_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(10)
        self.current_output_path_label.setFont(font)

        layout.addWidget(self.path_selector_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.current_output_path_label)
        self.setLayout(layout)

    def handleAudioFilePathSelected(self):
        file_dialog_options = QFileDialog.Options()
        file_dialog_options |= QFileDialog.DontUseNativeDialog
        selected_output_path = QFileDialog.getExistingDirectory(
            self, "Choose output path", options=file_dialog_options
        )
        if selected_output_path:
            printed_path = (
                (selected_output_path[:30] + "...")
                if len(selected_output_path) > 30
                else selected_output_path
            )
            text_in_HTML_format = f"""<p>Current output path: {printed_path}</p>"""
            self.current_output_path_label.setText(text_in_HTML_format)
            set_output_path(selected_output_path)


def start_application(user_webcams_count=0):
    app = QApplication(sys.argv)
    window = MainApplicationWindow()
    window.showMaximized()
    sys.exit(app.exec_())


start_application(0)
