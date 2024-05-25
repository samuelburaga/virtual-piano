import platform
import subprocess
import os


def open_folder(path):
    path = os.path.normpath(path)
    system = platform.system()

    if system == "Windows":
        subprocess.run(["explorer", path])
    elif system == "Linux":
        subprocess.run(["xdg-open", path])
    elif system == "Darwin":
        subprocess.run(["open", path])
    else:
        raise OSError(f"Unsupported operating system: {system}")
