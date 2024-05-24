from utils.webcam_utils import detect_number_of_webcams
from app import start
from virtual_piano.user_interface import *


def main():
    user_webcams_count = detect_number_of_webcams()
    start(user_webcams_count)


main()
