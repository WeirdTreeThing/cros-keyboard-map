#!/usr/bin/env python3

import argparse

vivaldi_keys = {
    "90": "previoussong",
    "91": "zoom",
    "92": "scale",
    "93": "print",
    "94": "brightnessdown",
    "95": "brightnessup",
    "97": "kbdillumdown",
    "98": "kbdillumup",
    "99": "nextsong",
    "9A": "playpause",
    "9B": "micmute",
    "9E": "kbdillumtoggle",
    "A0": "mute",
    "AE": "volumedown",
    "B0": "volumeup",
    "E9": "forward",
    "EA": "back",
    "E7": "refresh",
}

def get_physmap_data():
    try:
        with open("/sys/bus/platform/devices/i8042/serio0/function_row_physmap", "r") as file:
            return file.read().strip().split()
    except FileNotFoundError:
        return ""

def get_functional_row(physmap, use_vivaldi, super_is_held, super_inverted):
    i = 0
    result = ""
    for scancode in physmap:
        i += 1
        # Map zoom to f11 since most applications wont listen to zoom
        mapping = "f11" if vivaldi_keys[scancode] == "zoom" \
            else vivaldi_keys[scancode]

        match [super_is_held, use_vivaldi, super_inverted]:
            case [True, True, False] | [False, True, True]:
                result += f"{vivaldi_keys[scancode]} = f{i}\n"
            case [True, False, False] | [False, False, True]:
                result += f"f{i} = f{i}\n"
            case [False, True, False] | [True, True, True]:
                result += f"{vivaldi_keys[scancode]} = {mapping}\n"
            case [False, False, False] | [True, False, True]:
                result += f"f{i} = {mapping}\n"

    return result

def get_keyd_config(physmap, inverted):
    config = f"""\
[ids]
k:0001:0001
k:0000:0000

[main]
{get_functional_row(physmap, use_vivaldi=False, super_is_held=False, super_inverted=inverted)}
{get_functional_row(physmap, use_vivaldi=True, super_is_held=False, super_inverted=inverted)}
f13=coffee
sleep=coffee

[meta]
{get_functional_row(physmap, use_vivaldi=False, super_is_held=True, super_inverted=inverted)}
{get_functional_row(physmap, use_vivaldi=True, super_is_held=True, super_inverted=inverted)}

[alt]
backspace = delete
brightnessdown = kbdillumdown
brightnessup = kbdillumup
f6 = kbdillumdown
f7 = kbdillumup

[control]
f5 = print
scale = print

[control+alt]
backspace = C-A-delete
"""
    return config

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", default="cros.conf", help="path to save config (default: cros.conf)")
    parser.add_argument("-i", "--inverted", action="store_true", 
                        help="use functional keys by default and media keys when super is held")
    args = vars(parser.parse_args())

    physmap = get_physmap_data()
    if not physmap:
        print("no function row mapping found, using default mapping")
        physmap = ['EA', 'E9', 'E7', '91', '92', '94', '95', 'A0', 'AE', 'B0']
    
    config = get_keyd_config(physmap, args["inverted"])
    with open(args["file"], "w") as conf:
        conf.write(config)

if __name__ == "__main__":
    main()
