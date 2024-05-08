import yaml
import os

from dotenv import load_dotenv
from pathlib import Path


def load_configuration():
    load_dotenv()
    with open(
        os.environ["CONFIGURATION_FILE_PATH"].replace("ROOT_PATH", str(Path.home())),
        "r",
    ) as file:
        configuration = yaml.safe_load(file)
    return configuration


load_configuration()
