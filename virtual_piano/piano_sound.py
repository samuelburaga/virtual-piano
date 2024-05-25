import tinysoundfont

from constants import WHITE_KEYS_SOUNDS, BLACK_KEYS_SOUNDS, KeyTypeEnum

synth = tinysoundfont.Synth()


already_played_white_key = [False] * len(WHITE_KEYS_SOUNDS)
already_played_black_key = [False] * len(BLACK_KEYS_SOUNDS)

last_white_key_played = -1
last_black_key_played = -1


def start_piano():
    sfid = synth.sfload("assets/soundfonts/000_Florestan_Piano.sf2")
    synth.program_select(0, sfid, 0, 0)
    synth.start()


def play_note(key_type, index):
    global already_played_white_key, already_played_black_key
    global last_white_key_played, last_black_key_played

    if key_type == KeyTypeEnum.WHITE_KEY:
        if already_played_white_key[index] is False:
            synth.noteon(0, WHITE_KEYS_SOUNDS[index], 100)
            if last_white_key_played > -1:
                already_played_white_key[last_white_key_played] = False
            already_played_white_key[index] = True
            last_white_key_played = index
        if last_black_key_played > -1:
            already_played_black_key[last_black_key_played] = False
    else:
        if already_played_black_key[index] is False:
            synth.noteon(0, BLACK_KEYS_SOUNDS[index], 100)
            if last_black_key_played > -1:
                already_played_black_key[last_black_key_played] = False
            already_played_black_key[index] = True
            last_black_key_played = index
        if last_white_key_played > -1:
            already_played_white_key[last_white_key_played] = False


def set_keys_status_to_not_played():
    if last_white_key_played > -1:
        already_played_white_key[last_white_key_played] = False
    if last_black_key_played > -1:
        already_played_black_key[last_black_key_played] = False
