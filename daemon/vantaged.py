#!/usr/bin/env python3
import sys
import os

# Add parent dir to path so we can import features and ipc
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dbus
import dbus.mainloop.glib
from gi.repository import GLib
from ipc.dbus_service import VantageService

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    try:
        bus = dbus.SystemBus()
    except Exception as e:
        print(f"Error connecting to system bus: {e}")
        sys.exit(1)

    try:
        name = dbus.service.BusName("org.lenovo.Vantage", bus)
    except Exception as e:
        print(f"Error requesting name on D-Bus: {e}")
        sys.exit(1)

    service = VantageService(bus)
    print("Lenovo Vantage Daemon running...")

    from automation import AutomationEngine
    engine = AutomationEngine(service)
    engine.start()

    loop = GLib.MainLoop()
    try:
        loop.run()
    except KeyboardInterrupt:
        print("Exiting...")
        engine.stop()
        sys.exit(0)

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("Must be run as root!")
        sys.exit(1)
    main()
