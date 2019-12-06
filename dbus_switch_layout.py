#!/usr/bin/env python3

import dbus
import os
from inotify_simple import INotify, flags

bus = dbus.SessionBus()
service = bus.get_object('ru.gentoo.KbddService', '/ru/gentoo/KbddService')
next_layout = service.get_dbus_method('next_layout', 'ru.gentoo.kbdd')

directory = '/tmp/inotify_test'
if not os.path.exists(directory):
    os.makedirs(directory)

inotify = INotify()
watch_flags = flags.CREATE | flags.DELETE | flags.MODIFY | flags.DELETE_SELF
wd = inotify.add_watch('/tmp/inotify_test', watch_flags)


while True:
    for event in inotify.read():
        next_layout()
