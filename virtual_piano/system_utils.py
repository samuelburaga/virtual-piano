import platform
import subprocess


def open_folder(path):
    system = platform.system()

    if system == "Windows":
        subprocess.run(["explorer", path])
    elif system == "Linux":
        subprocess.run(["xdg-open", path])
    elif system == "Darwin":
        subprocess.run(["open", path])
    else:
        raise OSError(f"Unsupported operating system: {system}")
