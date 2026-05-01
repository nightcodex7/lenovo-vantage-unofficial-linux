import dbus
import dbus.service

class VantageService(dbus.service.Object):
    BUS_NAME = "org.lenovo.Vantage"
    OBJ_PATH = "/org/lenovo/Vantage"

    def __init__(self, bus):
        super().__init__(bus, self.OBJ_PATH)

    @dbus.service.method(BUS_NAME, in_signature="s", out_signature="")
    def SetPowerMode(self, mode):
        from features.power import set_power_mode
        set_power_mode(str(mode))

    @dbus.service.method(BUS_NAME, in_signature="", out_signature="s")
    def GetPowerMode(self):
        from features.power import get_power_mode
        return get_power_mode()

    @dbus.service.method(BUS_NAME, in_signature="s", out_signature="")
    def SetFanMode(self, mode):
        from features.fan import set_fan_mode
        set_fan_mode(str(mode))

    @dbus.service.method(BUS_NAME, in_signature="", out_signature="s")
    def GetFanMode(self):
        from features.fan import get_fan_mode
        return get_fan_mode()

    @dbus.service.method(BUS_NAME, in_signature="b", out_signature="")
    def SetConservation(self, enabled):
        from features.battery import set_conservation
        set_conservation(bool(enabled))

    @dbus.service.method(BUS_NAME, in_signature="", out_signature="b")
    def GetConservation(self):
        from features.battery import get_conservation
        return get_conservation()

    @dbus.service.method(BUS_NAME, in_signature="b", out_signature="")
    def SetUsbCharging(self, enabled):
        from features.battery import set_usb_charging
        set_usb_charging(bool(enabled))

    @dbus.service.method(BUS_NAME, in_signature="", out_signature="b")
    def GetUsbCharging(self):
        from features.battery import get_usb_charging
        return get_usb_charging()

    @dbus.service.method(BUS_NAME, in_signature="b", out_signature="")
    def SetFnLock(self, state):
        from features.system import set_fn_lock
        set_fn_lock(bool(state))

    @dbus.service.method(BUS_NAME, in_signature="", out_signature="b")
    def GetFnLock(self):
        from features.system import get_fn_lock
        return bool(get_fn_lock())

    @dbus.service.method(BUS_NAME, in_signature="b", out_signature="")
    def SetFlipToStart(self, state):
        from features.system import set_flip_to_start
        set_flip_to_start(bool(state))

    @dbus.service.method(BUS_NAME, in_signature="", out_signature="b")
    def GetFlipToStart(self):
        from features.system import get_flip_to_start
        return bool(get_flip_to_start())

    @dbus.service.method(BUS_NAME, in_signature="b", out_signature="")
    def SetInstantBoot(self, state):
        from features.system import set_instant_boot
        set_instant_boot(bool(state))

    @dbus.service.method(BUS_NAME, in_signature="", out_signature="b")
    def GetInstantBoot(self):
        from features.system import get_instant_boot
        return bool(get_instant_boot())

    @dbus.service.method(BUS_NAME, in_signature="iii", out_signature="b")
    def SetRyzenTdp(self, stapm, fast, slow):
        from features.power import set_ryzen_tdp
        return set_ryzen_tdp(int(stapm), int(fast), int(slow))

    @dbus.service.method(BUS_NAME, in_signature="", out_signature="a{sv}")
    def GetRyzenTdp(self):
        from features.power import get_ryzen_tdp
        tdp = get_ryzen_tdp()
        return dbus.Dictionary({
            "stapm": dbus.Int32(tdp["stapm"]),
            "fast": dbus.Int32(tdp["fast"]),
            "slow": dbus.Int32(tdp["slow"]),
            "supported": dbus.Boolean(tdp["supported"])
        }, signature='sv')

    @dbus.service.method(BUS_NAME, in_signature="s", out_signature="")
    def SetDgpuMode(self, mode):
        from features.gpu import set_dgpu_mode
        set_dgpu_mode(str(mode))

    @dbus.service.method(BUS_NAME, in_signature="", out_signature="s")
    def GetDgpuMode(self):
        from features.gpu import get_dgpu_mode
        return get_dgpu_mode()

    @dbus.service.method(BUS_NAME, in_signature="", out_signature="a{sv}")
    def GetSensors(self):
        from features.sensors import get_cpu_temp, get_gpu_temp, get_cpu_usage, get_gpu_usage, get_fan_rpm
        from features.battery import get_battery_info
        
        info = {
            "cpu_temp": dbus.Double(get_cpu_temp()),
            "gpu_temp": dbus.Double(get_gpu_temp()),
            "cpu_usage": dbus.Double(get_cpu_usage()),
            "gpu_usage": dbus.Double(get_gpu_usage()),
            "fan_rpm": dbus.Int32(get_fan_rpm())
        }
        
        bat_info = get_battery_info()
        for k, v in bat_info.items():
            if isinstance(v, int):
                info[f"bat_{k}"] = dbus.Int32(v)
            else:
                info[f"bat_{k}"] = dbus.String(v)
                
        return dbus.Dictionary(info, signature='sv')

    @dbus.service.method(BUS_NAME, in_signature="", out_signature="a{sa{sv}}")
    def GetAllCapabilities(self):
        from features.power import detect_capabilities as cap_power
        from features.gpu import detect_capabilities as cap_gpu
        from features.fan import detect_capabilities as cap_fan
        from features.battery import detect_capabilities as cap_bat
        from features.system import detect_capabilities as cap_sys
        from features.sensors import detect_capabilities as cap_sens
        from features.rgb import detect_capabilities as cap_rgb
        from features.overclock import detect_capabilities as cap_oc

        def dict_to_dbus(d):
            return dbus.Dictionary({
                "supported": dbus.Boolean(d.get("supported", False)),
                "partial": dbus.Boolean(d.get("partial", False)),
                "reason": dbus.String(d.get("reason", ""))
            }, signature='sv')

        return dbus.Dictionary({
            "power": dict_to_dbus(cap_power()),
            "gpu": dict_to_dbus(cap_gpu()),
            "fan": dict_to_dbus(cap_fan()),
            "battery": dict_to_dbus(cap_bat()),
            "system": dict_to_dbus(cap_sys()),
            "sensors": dict_to_dbus(cap_sens()),
            "rgb": dict_to_dbus(cap_rgb()),
            "overclock": dict_to_dbus(cap_oc())
        }, signature='sa{sv}')

    @dbus.service.method(BUS_NAME, in_signature="ii", out_signature="b")
    def SetGpuClocks(self, core, mem):
        from features.overclock import set_gpu_clocks
        return set_gpu_clocks(int(core), int(mem))

    @dbus.service.method(BUS_NAME, in_signature="ss", out_signature="")
    def SetRgbMode(self, mode, color):
        from features.rgb import set_rgb_mode
        set_rgb_mode(str(mode), str(color))

    @dbus.service.method(BUS_NAME, in_signature="sa{ss}", out_signature="")
    def SetAutomationRule(self, event_name, rule_dict):
        import json, os
        from pathlib import Path
        CONFIG_FILE = "/etc/lenovo-vantage/automation.json"
        try:
            rules = json.loads(Path(CONFIG_FILE).read_text()) if Path(CONFIG_FILE).exists() else {}
            rules[str(event_name)] = {str(k): str(v) for k, v in rule_dict.items()}
            os.makedirs("/etc/lenovo-vantage", exist_ok=True)
            Path(CONFIG_FILE).write_text(json.dumps(rules, indent=4))
        except Exception:
            pass

    @dbus.service.method(BUS_NAME, in_signature="s", out_signature="a{ss}")
    def GetAutomationRule(self, event_name):
        import json
        from pathlib import Path
        CONFIG_FILE = "/etc/lenovo-vantage/automation.json"
        try:
            if Path(CONFIG_FILE).exists():
                rules = json.loads(Path(CONFIG_FILE).read_text())
                return dbus.Dictionary({k: dbus.String(v) for k, v in rules.get(str(event_name), {}).items()}, signature='ss')
        except Exception:
            pass
        return dbus.Dictionary({}, signature='ss')
