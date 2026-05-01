#!/usr/bin/env python3
import sys
import argparse
import dbus

def get_service():
    try:
        bus = dbus.SystemBus()
        obj = bus.get_object("org.lenovo.Vantage", "/org/lenovo/Vantage")
        return dbus.Interface(obj, "org.lenovo.Vantage")
    except dbus.exceptions.DBusException as e:
        print(f"Error connecting to Vantage daemon: {e}", file=sys.stderr)
        print("Is the vantaged service running?", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Lenovo Vantage CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Power Mode
    pm_parser = subparsers.add_parser("power", help="Get or set power mode")
    pm_parser.add_argument("mode", nargs="?", choices=["quiet", "balanced", "performance"], help="Set power mode")

    # Fan Mode
    fm_parser = subparsers.add_parser("fan", help="Get or set fan mode")
    fm_parser.add_argument("mode", nargs="?", choices=["super_silent", "standard", "dust_cleaning", "performance"], help="Set fan mode")

    # Battery
    bat_parser = subparsers.add_parser("battery", help="Get or set battery conservation")
    bat_parser.add_argument("state", nargs="?", choices=["on", "off"], help="Set conservation mode")

    # USB
    usb_parser = subparsers.add_parser("usb", help="Get or set USB always-on charging")
    usb_parser.add_argument("state", nargs="?", choices=["on", "off"], help="Set USB charging")

    # Fn Lock
    fn_parser = subparsers.add_parser("fnlock", help="Get or set Fn lock")
    fn_parser.add_argument("state", nargs="?", choices=["on", "off"], help="Set Fn lock")

    # GPU
    gpu_parser = subparsers.add_parser("gpu", help="Get or set dGPU mode")
    gpu_parser.add_argument("mode", nargs="?", choices=["integrated", "hybrid", "dedicated"], help="Set dGPU mode")

    # TDP
    tdp_parser = subparsers.add_parser("tdp", help="Set Ryzen CPU TDP via ryzenadj")
    tdp_parser.add_argument("stapm", type=int, help="STAPM Limit in mW")
    tdp_parser.add_argument("fast", type=int, help="Fast Limit in mW")
    tdp_parser.add_argument("slow", type=int, help="Slow Limit in mW")

    # Sensors
    subparsers.add_parser("sensors", help="Show sensor data")

    # Automation
    auto_parser = subparsers.add_parser("automation", help="Get or set automation rule")
    auto_parser.add_argument("event", choices=["on_ac_connect", "on_ac_disconnect"], help="Event name")
    auto_parser.add_argument("--power", help="Set power mode on event")
    auto_parser.add_argument("--gpu", help="Set GPU mode on event")

    # RGB
    rgb_parser = subparsers.add_parser("rgb", help="Set RGB lighting (via OpenRGB)")
    rgb_parser.add_argument("mode", choices=["static", "breathing", "rainbow", "off"], help="RGB Mode")
    rgb_parser.add_argument("--color", default="FF0000", help="Hex color code (e.g. FF0000)")

    # Overclocking
    oc_parser = subparsers.add_parser("overclock", help="Set GPU Overclock offsets")
    oc_parser.add_argument("core", type=int, help="Core clock offset")
    oc_parser.add_argument("mem", type=int, help="Memory clock offset")

    # Capabilities
    subparsers.add_parser("capabilities", help="Show hardware capabilities")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    svc = get_service()

    if args.command == "power":
        if args.mode:
            svc.SetPowerMode(args.mode)
        else:
            print(svc.GetPowerMode())

    elif args.command == "fan":
        if args.mode:
            svc.SetFanMode(args.mode)
        else:
            print(svc.GetFanMode())

    elif args.command == "battery":
        if args.state:
            svc.SetConservation(args.state == "on")
        else:
            print("On" if svc.GetConservation() else "Off")

    elif args.command == "usb":
        if args.state:
            svc.SetUsbCharging(args.state == "on")
        else:
            print("On" if svc.GetUsbCharging() else "Off")

    elif args.command == "fnlock":
        if args.state:
            svc.SetFnLock(args.state == "on")
        else:
            print("On" if svc.GetFnLock() else "Off")

    elif args.command == "gpu":
        if args.mode:
            try:
                svc.SetDgpuMode(args.mode)
            except Exception as e:
                print(f"Failed to toggle dGPU mode: {e}")
        else:
            print(svc.GetDgpuMode().capitalize())

    elif args.command == "tdp":
        success = svc.SetRyzenTdp(args.stapm, args.fast, args.slow)
        if success:
            print("TDP limits applied successfully.")
        else:
            print("Failed to apply TDP limits. Is ryzenadj installed?", file=sys.stderr)

    elif args.command == "sensors":
        sensors = svc.GetSensors()
        print(f"CPU Temp:  {sensors.get('cpu_temp', 0):.1f}°C")
        print(f"CPU Usage: {sensors.get('cpu_usage', 0):.1f}%")
        print(f"GPU Temp:  {sensors.get('gpu_temp', 0):.1f}°C")
        print(f"GPU Usage: {sensors.get('gpu_usage', 0):.1f}%")
        print(f"Fan RPM:   {sensors.get('fan_rpm', 0)}")
        print(f"Battery:   {sensors.get('bat_capacity', 0)}% ({sensors.get('bat_status', 'Unknown')})")

    elif args.command == "rgb":
        svc.SetRgbMode(args.mode, args.color)

    elif args.command == "automation":
        if args.power or args.gpu:
            rule = {}
            if args.power: rule["power_mode"] = args.power
            if args.gpu: rule["gpu_mode"] = args.gpu
            svc.SetAutomationRule(args.event, dbus.Dictionary(rule, signature='ss'))
            print(f"Set rule {args.event} -> {rule}")
        else:
            rule = svc.GetAutomationRule(args.event)
            print(f"{args.event}: {dict(rule)}")

    elif args.command == "overclock":
        if svc.SetGpuClocks(args.core, args.mem):
            print("GPU Overclock applied successfully.")
        else:
            print("Failed to apply GPU Overclock. Is nvidia-settings installed and Coolbits enabled?", file=sys.stderr)

    elif args.command == "capabilities":
        caps = svc.GetAllCapabilities()
        for k, v in caps.items():
            print(f"{k.capitalize()}:")
            print(f"  Supported: {bool(v.get('supported', False))}")
            print(f"  Partial:   {bool(v.get('partial', False))}")
            print(f"  Reason:    {str(v.get('reason', ''))}")

if __name__ == "__main__":
    main()
