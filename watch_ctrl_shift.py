#!/usr/bin/env python3

import keyboard

def switch_layout():
    # print("11")
    with open("/tmp/inotify_test/1.txt", "w") as f:
        f.write("")

keyboard.add_hotkey('ctrl+shift', switch_layout)
keyboard.wait()


