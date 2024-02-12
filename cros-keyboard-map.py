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

def load_physmap_data():
    try:
        with open("/sys/bus/platform/devices/i8042/serio0/function_row_physmap", "r") as file:
            return file.read().strip().split()
    except FileNotFoundError:
        return ""

def create_keyd_config(physmap):
    config = ""
    config += """[ids]
k:0001:0001
k:0000:0000

[main]
"""
    # make fn keys act like vivaldi keys when super isn't held
    i = 0
    for scancode in physmap:
        i += 1
        # Map zoom to f11 since most applications wont listen to zoom
        if vivaldi_keys[scancode] == "zoom":
            mapping = "f11"
        else:
            mapping = vivaldi_keys[scancode]
        config += f"f{i} = {mapping}\n"
    config += "\n"
    
    # make vivaldi keys act like vivaldi keys when super isn't held
    for scancode in physmap:
        # Map zoom to f11 since most applications wont listen to zoom
        if vivaldi_keys[scancode] == "zoom":
            mapping = "f11"
        else:
            mapping = vivaldi_keys[scancode]
        config += f"{vivaldi_keys[scancode]} = {mapping}\n"

    # map lock button to coffee
    config += "\nf13=coffee\nsleep=coffee\n"

    # make fn keys act like fn keys when super is held
    i = 0
    config += "\n[meta]\n"
    for scancode in physmap:
        i += 1
        config += f"f{i} = f{i}\n"

    # make vivaldi keys act like like fn keys when super is held
    i = 0
    config += "\n"
    for scancode in physmap:
        i += 1
        config += f"{vivaldi_keys[scancode]} = f{i}\n"

    # Add various extra shortcuts
    config += """\n[alt]
backspace = delete
brightnessdown = kbdillumdown
brightnessup = kbdillumup
f6 = kbdillumdown
f7 = kbdillumup

[control]
f5 = print
scale = print

[control+alt]
backspace = C-A-delete"""

    return config

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", default="cros.conf", help="path to save config (default: cros.conf)")
    args = vars(parser.parse_args())

    physmap = load_physmap_data()
    if not physmap:
        print("no function row mapping found, using default mapping")
        physmap = ['EA', 'E9', 'E7', '91', '92', '94', '95', 'A0', 'AE', 'B0']
    
    config = create_keyd_config(physmap)
    with open(args["file"], "w") as conf:
        conf.write(config)

if __name__ == "__main__":
    main()
