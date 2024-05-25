from webcam import detect_number_of_webcams
from user_interface import start_application


def main():
    user_webcams_count = detect_number_of_webcams()
    start_application(user_webcams_count)


main()
