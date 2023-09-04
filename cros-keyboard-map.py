#!/usr/bin/env python3

def vivaldi_scancode_to_keyd(scancode):
    match scancode:
        case "90":
            return "previoussong"
        case "91":
            return "zoom"
        case "92":
            return "scale"
        case "93":
            return "print"
        case "94":
            return "brightnessdown"
        case "95":
            return "brightnessup"
        case "97":
            return "kbdillumdown"
        case "98":
            return "kbdillumup"
        case "99":
            return "nextsong"
        case "9A":
            return "playpause"
        case "9B":
            return "micmute"
        case "9E":
            return "kbdillumtoggle"
        case "A0":
            return "mute"
        case "AE":
            return "volumedown"
        case "B0":
            return "volumeup"
        case "E9":
            return "forward"
        case "EA":
            return "back"
        case "E7":
            return "refresh"

def load_physmap_data():
    try:
        with open("/sys/bus/platform/devices/i8042/serio0/function_row_physmap", "r") as file:
            return file.read().strip().split()
    except FileNotFoundError:
        return ""

def create_keyd_config(physmap):
    config = ""
    config += """[ids]
0001:0001

[main]
"""
    # make fn keys act like vivaldi keys when super isn't held
    i = 0
    for scancode in physmap:
        i += 1
        # Map zoom to f11 since most applications wont listen to zoom
        if vivaldi_scancode_to_keyd(scancode) == "zoom":
            mapping = "f11"
        else:
            mapping = vivaldi_scancode_to_keyd(scancode)
        config += f"f{i} = {mapping}\n"
    config += "\n"
    
    # make vivaldi keys act like vivaldi keys when super isn't held
    i = 0
    for scancode in physmap:
        i += 1
        # Map zoom to f11 since most applications wont listen to zoom
        if vivaldi_scancode_to_keyd(scancode) == "zoom":
            mapping = "f11"
        else:
            mapping = vivaldi_scancode_to_keyd(scancode)
        config += f"{vivaldi_scancode_to_keyd(scancode)} = {mapping}\n"

    # map lock button to coffee
    config += "\nf13=coffee\nsleep=coffee\n"

    # make fn keys act like fn keys when super is held
    i = 0
    config += "\n[meta]\n"
    for scancode in physmap:
        i += 1
        config += f"f{i} = f{i}\n"

    # make lock buttons act like fn keys when super is held
    config +="\nf13=f13\nf12=f12\n"
    # make vivaldi keys act like like fn keys when super is held
    i = 0
    config += "\n"
    for scancode in physmap:
        i += 1
        config += f"{vivaldi_scancode_to_keyd(scancode)} = f{i}\n"

    # make lock buttons act like like fn keys when super is held
    config += "\nf13=f13\nsleep=f12\n"
    # Add various extra shortcuts
    config += """\n[alt]
backspace = delete
meta = capslock
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
    physmap = load_physmap_data()
    if not physmap:
        print("no function row mapping found, using default mapping")
        physmap = ['EA', 'E9', 'E7', '91', '92', '94', '95', 'A0', 'AE', 'B0']
    
    config = create_keyd_config(physmap)
    with open("cros.conf", "w") as conf:
        conf.write(config)

main()
