import cv2 as cv

video_recording = None


def start_video_recording(frame_rate, webcam_dimensions):
    global video_recording

    fourcc_code = cv.VideoWriter.fourcc(*"DIVX")
    video_recording = cv.VideoWriter(
        "out/video/video-recording.avi", fourcc_code, frame_rate, webcam_dimensions
    )


def write_frame(frame):
    global video_recording

    video_recording.write(frame)


def release_video_recording():
    global video_recording

    video_recording.release()
