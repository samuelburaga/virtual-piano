from utils.webcam_utils import detect_number_of_webcams
from app import start


def main():
    user_webcams_count = detect_number_of_webcams()
    start(user_webcams_count)


main()
