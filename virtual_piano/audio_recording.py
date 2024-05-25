import soundcard as sc
import soundfile as sf
from datetime import datetime
from constants import AUDIO_RECORDING_SAMPLE_RATE, DEFAULT_OUTPUT_ROOT_PATH

output_path = DEFAULT_OUTPUT_ROOT_PATH
default_output_path = output_path
is_recording = False


def get_default_output_path():
    global default_output_path
    return default_output_path


def change_recording_status():
    global is_recording
    is_recording = not is_recording


def get_recording_status():
    return is_recording


def set_output_path(selected_output_path):
    global output_path
    output_path = selected_output_path


def get_output_path():
    return output_path


def start_audio_recording():
    with sc.get_microphone(
        id=str(sc.default_speaker().name), include_loopback=True
    ).recorder(samplerate=AUDIO_RECORDING_SAMPLE_RATE) as mic:

        output_path = get_output_path()

        try:
            with sf.SoundFile(
                output_path
                + "/virtual-piano-audio-recording"
                + "_"
                + datetime.now().strftime("%y%m%d_%H%M%S")
                + ".wav",
                "w",
                samplerate=AUDIO_RECORDING_SAMPLE_RATE,
                channels=1,
            ) as file:
                while get_recording_status():
                    data = mic.record(numframes=AUDIO_RECORDING_SAMPLE_RATE)
                    file.write(data[:, 0])

        except:
            print("\nSomething went wrong while trying to record the audio!!!")
