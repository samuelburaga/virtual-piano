from utils.config_utils import load_configuration
from receiver import receive


def main():
    configuration = load_configuration()
    receive(configuration)


main()
