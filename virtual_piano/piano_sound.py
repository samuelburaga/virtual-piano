import tinysoundfont
import time

from constants import WHITE_KEYS_SOUNDS, BLACK_KEYS_SOUNDS, KeyTypeEnum

synth = tinysoundfont.Synth()


already_played_white_key = [False] * len(WHITE_KEYS_SOUNDS)
already_played_black_key = [False] * len(BLACK_KEYS_SOUNDS)

last_time_played_white_keys = [-1] * len(WHITE_KEYS_SOUNDS)
last_time_played_black_keys = [-1] * len(BLACK_KEYS_SOUNDS)

last_white_key_played = -1
last_black_key_played = -1

start_time = {}

WHITE_KEY_WAS_RELEASED = [True] * len(WHITE_KEYS_SOUNDS)
BLACK_KEY_WAS_RELEASED = [True] * len(BLACK_KEYS_SOUNDS)


def start_piano():
    global start_time
    start_time = time.time()
    sfid = synth.sfload("assets/soundfonts/000_Florestan_Piano.sf2")
    synth.program_select(0, sfid, 0, 0)
    synth.start()


def play_note(key_type, index):

    global WHITE_KEY_WAS_RELEASED
    global already_played_white_key, already_played_black_key
    global last_white_key_played, last_black_key_played

    if key_type == KeyTypeEnum.WHITE_KEY:
        if already_played_white_key[index] is False:
            WHITE_KEY_WAS_RELEASED[index] = False
            synth.noteon(0, WHITE_KEYS_SOUNDS[index], 100)
            last_time_played_white_keys[index] = time.time()
            if last_white_key_played > -1:
                already_played_white_key[last_white_key_played] = False
            already_played_white_key[index] = True
            last_white_key_played = index
        else:
            if (
                WHITE_KEY_WAS_RELEASED[index] is True
                and time.time() - last_time_played_white_keys[index] >= 0.2
            ):
                synth.noteon(0, WHITE_KEYS_SOUNDS[index], 100)
                last_time_played_white_keys[index] = time.time()
                WHITE_KEY_WAS_RELEASED[index] = False
                last_white_key_played = index

        if last_black_key_played > -1:
            already_played_black_key[last_black_key_played] = False
            BLACK_KEY_WAS_RELEASED[last_black_key_played] = True
    else:
        if already_played_black_key[index] is False:
            BLACK_KEY_WAS_RELEASED[index] = False
            synth.noteon(0, BLACK_KEYS_SOUNDS[index], 100)
            if last_black_key_played > -1:
                already_played_black_key[last_black_key_played] = False
            already_played_black_key[index] = True
            last_black_key_played = index
        else:
            if (
                BLACK_KEY_WAS_RELEASED[index] is True
                and time.time() - last_time_played_white_keys[index] >= 0.2
            ):
                synth.noteon(0, BLACK_KEYS_SOUNDS[index], 100)
                last_time_played_black_keys[index] = time.time()
                BLACK_KEY_WAS_RELEASED[index] = False
                last_black_key_played = index

        if last_white_key_played > -1:
            already_played_white_key[last_white_key_played] = False
            WHITE_KEY_WAS_RELEASED[last_white_key_played] = True


def set_keys_status_to_not_played():
    if last_white_key_played > -1:
        already_played_white_key[last_white_key_played] = False
    if last_black_key_played > -1:
        already_played_black_key[last_black_key_played] = False
