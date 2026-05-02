#!/usr/bin/env python3
import sys
import argparse
import dbus
import json

def get_service():
    try:
        bus = dbus.SystemBus()
        obj = bus.get_object("org.lenovo.Vantage", "/org/lenovo/Vantage")
        return dbus.Interface(obj, "org.lenovo.Vantage")
    except dbus.exceptions.DBusException as e:
        print(f"Error connecting to Vantage daemon: {e}", file=sys.stderr)
        print("Is the vantaged service running?", file=sys.stderr)
        sys.exit(1)

def dbus_to_py(obj):
    if isinstance(obj, dbus.Dictionary):
        return {str(k): dbus_to_py(v) for k, v in obj.items()}
    elif isinstance(obj, dbus.Array):
        return [dbus_to_py(v) for v in obj]
    elif isinstance(obj, dbus.String):
        return str(obj)
    elif isinstance(obj, dbus.Boolean):
        return bool(obj)
    elif isinstance(obj, (dbus.Int32, dbus.Int64, dbus.UInt32, dbus.UInt64, dbus.Byte)):
        return int(obj)
    elif isinstance(obj, dbus.Double):
        return float(obj)
    return obj

def main():
    parser = argparse.ArgumentParser(description="Lenovo Vantage CLI")
    parser.add_argument("--json", "-j", action="store_true", help="Output in JSON format")
    parser.add_argument("--version", "-v", action="version", version="%(prog)s 1.0.0")
    
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
    tdp_parser.add_argument("--stapm", type=int, required=True, help="STAPM Limit in mW (e.g. 45000 = 45 W)")
    tdp_parser.add_argument("--fast", type=int, required=True, help="Fast Limit in mW")
    tdp_parser.add_argument("--slow", type=int, required=True, help="Slow Limit in mW")

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
            if args.json: print(json.dumps({"status": "success", "power_mode": args.mode}))
        else:
            mode = str(svc.GetPowerMode())
            if args.json: print(json.dumps({"power_mode": mode}))
            else: print(mode.capitalize())

    elif args.command == "fan":
        if args.mode:
            svc.SetFanMode(args.mode)
            if args.json: print(json.dumps({"status": "success", "fan_mode": args.mode}))
        else:
            mode = str(svc.GetFanMode())
            if args.json: print(json.dumps({"fan_mode": mode}))
            else: print(mode.replace("_", " ").title())

    elif args.command == "battery":
        if args.state:
            state_bool = args.state == "on"
            svc.SetConservation(state_bool)
            if args.json: print(json.dumps({"status": "success", "conservation": state_bool}))
        else:
            state = bool(svc.GetConservation())
            if args.json: print(json.dumps({"conservation": state}))
            else: print("On" if state else "Off")

    elif args.command == "usb":
        if args.state:
            state_bool = args.state == "on"
            svc.SetUsbCharging(state_bool)
            if args.json: print(json.dumps({"status": "success", "always_on_usb": state_bool}))
        else:
            state = bool(svc.GetUsbCharging())
            if args.json: print(json.dumps({"always_on_usb": state}))
            else: print("On" if state else "Off")

    elif args.command == "fnlock":
        if args.state:
            state_bool = args.state == "on"
            svc.SetFnLock(state_bool)
            if args.json: print(json.dumps({"status": "success", "fn_lock": state_bool}))
        else:
            state = bool(svc.GetFnLock())
            if args.json: print(json.dumps({"fn_lock": state}))
            else: print("On" if state else "Off")

    elif args.command == "gpu":
        if args.mode:
            try:
                svc.SetDgpuMode(args.mode)
                if args.json: print(json.dumps({"status": "success", "gpu_mode": args.mode}))
            except Exception as e:
                if args.json: print(json.dumps({"status": "error", "message": str(e)}))
                else: print(f"Failed to toggle dGPU mode: {e}")
        else:
            mode = str(svc.GetDgpuMode())
            if args.json: print(json.dumps({"gpu_mode": mode}))
            else: print(mode.capitalize())

    elif args.command == "tdp":
        success = svc.SetRyzenTdp(args.stapm, args.fast, args.slow)
        if args.json:
            print(json.dumps({"status": "success" if success else "error"}))
        else:
            if success:
                print("TDP limits applied successfully.")
            else:
                print("Failed to apply TDP limits. Is ryzenadj installed?", file=sys.stderr)

    elif args.command == "sensors":
        raw_sensors = svc.GetSensors()
        sensors = dbus_to_py(raw_sensors)
        if args.json:
            print(json.dumps(sensors, indent=2))
        else:
            print(f"{'CPU Temp:':<12} {sensors.get('cpu_temp', 0):.1f}°C")
            print(f"{'CPU Usage:':<12} {sensors.get('cpu_usage', 0):.1f}%")
            print(f"{'GPU Temp:':<12} {sensors.get('gpu_temp', 0):.1f}°C")
            print(f"{'GPU Usage:':<12} {sensors.get('gpu_usage', 0):.1f}%")
            print(f"{'Fan RPM:':<12} {sensors.get('fan_rpm', 0)}")
            print(f"{'Battery:':<12} {sensors.get('bat_capacity', 0)}% ({sensors.get('bat_status', 'Unknown')})")

    elif args.command == "rgb":
        svc.SetRgbMode(args.mode, args.color)
        if args.json: print(json.dumps({"status": "success"}))

    elif args.command == "automation":
        if args.power or args.gpu:
            rule = {}
            if args.power: rule["power_mode"] = args.power
            if args.gpu: rule["gpu_mode"] = args.gpu
            svc.SetAutomationRule(args.event, dbus.Dictionary(rule, signature='ss'))
            if args.json: print(json.dumps({"status": "success", "event": args.event, "rule": rule}))
            else: print(f"Set rule {args.event} -> {rule}")
        else:
            raw_rule = svc.GetAutomationRule(args.event)
            rule = dbus_to_py(raw_rule)
            if args.json: print(json.dumps({args.event: rule}))
            else: print(f"{args.event}: {rule}")

    elif args.command == "overclock":
        if svc.SetGpuClocks(args.core, args.mem):
            if args.json: print(json.dumps({"status": "success"}))
            else: print("GPU Overclock applied successfully.")
        else:
            if args.json: print(json.dumps({"status": "error", "message": "Failed to apply GPU Overclock."}))
            else: print("Failed to apply GPU Overclock. Is nvidia-settings installed and Coolbits enabled?", file=sys.stderr)

    elif args.command == "capabilities":
        raw_caps = svc.GetAllCapabilities()
        caps = dbus_to_py(raw_caps)
        if args.json:
            print(json.dumps(caps, indent=2))
        else:
            for k, v in caps.items():
                sup = bool(v.get('supported', False))
                part = bool(v.get('partial', False))
                reason = str(v.get('reason', ''))
                mark = "[✓]" if sup else ("[~]" if part else "[✗]")
                print(f"{mark} {k.capitalize()}:")
                print(f"  Supported: {sup}")
                print(f"  Partial:   {part}")
                if reason:
                    print(f"  Reason:    {reason}")

if __name__ == "__main__":
    main()
