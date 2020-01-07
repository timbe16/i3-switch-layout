#!/usr/bin/env python3

# source https://blog.robertelder.org/detect-keyup-event-linux-terminal/

import os
import signal
import re
import threading
import time
import struct
import xkbgroup

class LeftCtrlShiftKeyEventClass(object):
  def __init__(self):
    self.done = False
    self.leftCtrlPressed = False
    self.leftShiftPressed = False
    self.leftCtrlReleased = False
    self.leftShiftReleased = False
    self.numLeftCtrlCode = 29
    self.numLeftShiftCode = 42
    self.xkb = xkbgroup.XKeyboard()
    signal.signal(signal.SIGINT, self.cleanup)

    with open('/proc/bus/input/devices') as f:
      devices_file_contents = f.read()

    for handlers in re.findall(r"""H: Handlers=([^\n]+)""", devices_file_contents, re.DOTALL):
      dev_event_file = '/dev/input/event' + re.search(r'event(\d+)', handlers).group(1)
      if 'kbd' in handlers:
        t = threading.Thread(target=self.read_events, kwargs={'dev_event_file': dev_event_file})
        t.daemon = True
        t.start()

    while not self.done: #  Wait for Ctrl+C
      time.sleep(1)

  def cleanup(self, signum, frame):
    self.done = True

  def resetCtrlShift(self):
    self.leftCtrlPressed = False
    self.leftShiftPressed = False
    self.leftCtrlReleased = False
    self.leftShiftReleased = False

  def switch_layout(self):
      print("Switching layout..")
      self.resetCtrlShift()
      layouts = self.xkb.groups_names
      print(layouts)
      current_layout = self.xkb.group_name
      layouts.remove(current_layout)
      print(layouts)
      if len(layouts) != 1:
        print("err: ", layouts)
      next_layout = layouts.pop()
      print("Current layout: ", current_layout)
      print("Next layout: ", next_layout)
      self.xkb.group_name = next_layout

  def read_events(self, dev_event_file):
    print("Listening for kbd events on dev_event_file=" + str(dev_event_file))
    try:
      of = open(dev_event_file, 'rb')
    except IOError as e:
      if e.strerror == 'Permission denied':
        print("You don't have read permission on ({}). Are you root?".format(dev_event_file))
        return
    while True:
      event_bin_format = 'llHHI'  #  See kernel documentation for 'struct input_event'
      #  For details, read section 5 of this document:
      #  https://www.kernel.org/doc/Documentation/input/input.txt
      data = of.read(struct.calcsize(event_bin_format))
      seconds, microseconds, e_type, code, value = struct.unpack(event_bin_format, data)
      full_time = seconds + microseconds / 1000000
      if e_type == 0x1:  #  0x1 == EV_KEY means key press or release.
        # d = ("RELEASE" if value == 0 else "PRESS")  #  value == 0 release, value == 1 press
        # print("Got key " + d + " from " + str(dev_event_file) + ": t=" + str(full_time) + "us type=" + str(e_type) + " code=" + str(code))
        if value == 1 and code == self.numLeftCtrlCode:
            self.leftCtrlPressed = True
        elif value == 0 and code == self.numLeftCtrlCode:
            self.leftCtrlReleased = True
        elif value == 1 and code == self.numLeftShiftCode and self.leftCtrlPressed:
            self.leftShiftPressed = True
        elif value == 0 and code == self.numLeftShiftCode and self.leftCtrlPressed:
            self.leftShiftReleased = True
        else:
            self.resetCtrlShift()

        if self.leftCtrlPressed and self.leftCtrlReleased and self.leftShiftPressed and self.leftShiftReleased:
            self.switch_layout()



a = LeftCtrlShiftKeyEventClass()
