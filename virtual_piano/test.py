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
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap


class WebcamWidget(QWidget):
    def __init__(self):
        super().__init__()

        # Set up the UI
        self.setWindowTitle("PyQt5 OpenCV Webcam Example")
        self.layout = QVBoxLayout()

        # Add a label to display the webcam feed
        self.video_label = QLabel(self)
        self.layout.addWidget(self.video_label)

        # Add a button to close the application
        self.quit_button = QPushButton("Quit")
        self.quit_button.clicked.connect(self.close_application)
        self.layout.addWidget(self.quit_button)

        self.setLayout(self.layout)

        # Set up a QTimer to periodically update the frame
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30 ms

        # Initialize the webcam
        self.cap = cv2.VideoCapture(0)

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Draw a rectangle on the frame
            cv2.rectangle(frame, (100, 100), (300, 300), (255, 0, 0), 3)

            # Draw text on the frame
            cv2.putText(
                frame,
                "Hello, OpenCV!",
                (100, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )

            # Convert the frame to RGB format
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            step = channel * width
            qimg = QImage(frame.data, width, height, step, QImage.Format_RGB888)
            self.video_label.setPixmap(QPixmap.fromImage(qimg))

    def close_application(self):
        self.cap.release()
        self.close()

    def closeEvent(self, event):
        self.cap.release()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebcamWidget()
    window.showMaximized()  # Show the window maximized
    sys.exit(app.exec_())
