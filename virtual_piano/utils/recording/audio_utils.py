import soundcard as sc
import soundfile as sf
import keyboard

from constants.constants import AUDIO_RECORDING_SAMPLE_RATE


def start_audio_recording():
    with sc.get_microphone(
        id=str(sc.default_speaker().name), include_loopback=True
    ).recorder(samplerate=AUDIO_RECORDING_SAMPLE_RATE) as mic:
        print("Recording audio...")
        try:
            with sf.SoundFile(
                "out/audio/audio-recording.wav",
                "w",
                samplerate=AUDIO_RECORDING_SAMPLE_RATE,
                channels=1,
            ) as file:
                while True:
                    data = mic.record(numframes=AUDIO_RECORDING_SAMPLE_RATE)
                    file.write(data[:, 0])
                    if keyboard.is_pressed("q"):  # Check if 'q' is pressed
                        break
        except KeyboardInterrupt:
            print("\nRecording stopped manually.")
