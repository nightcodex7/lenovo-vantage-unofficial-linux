import glob
from pathlib import Path

def get_vpc_path():
    vpc_paths = glob.glob("/sys/bus/platform/devices/VPC2004:*")
    return vpc_paths[0] if vpc_paths else None

def get_battery_path():
    for bat in ["BAT0", "BAT1", "BATT"]:
        if Path(f"/sys/class/power_supply/{bat}").exists():
            return f"/sys/class/power_supply/{bat}"
    return None

def detect_capabilities() -> dict:
    vpc = get_vpc_path()
    bat = get_battery_path()
    supported = vpc is not None and bat is not None
    return {
        "supported": supported,
        "partial": not supported,
        "reason": "Battery and VPC available" if supported else "Missing battery or VPC"
    }

def set_conservation(enabled: bool) -> None:
    vpc = get_vpc_path()
    if not vpc:
        raise FileNotFoundError("VPC device not found")
    Path(f"{vpc}/conservation_mode").write_text("1" if enabled else "0")

def get_conservation() -> bool:
    vpc = get_vpc_path()
    if not vpc:
        return False
    try:
        return Path(f"{vpc}/conservation_mode").read_text().strip() == "1"
    except FileNotFoundError:
        return False

def get_usb_charging() -> bool:
    vpc = get_vpc_path()
    if not vpc:
        return False
    try:
        return Path(f"{vpc}/usb_charging").read_text().strip() == "1"
    except FileNotFoundError:
        return False

def set_usb_charging(enabled: bool) -> None:
    vpc = get_vpc_path()
    if not vpc:
        raise FileNotFoundError("VPC device not found")
    Path(f"{vpc}/usb_charging").write_text("1" if enabled else "0")

def get_battery_info() -> dict:
    bat_path = get_battery_path()
    if not bat_path:
        return {}
    p = Path(bat_path)
        
    def read_safe(file, default=0, is_int=True):
        try:
            val = (p / file).read_text().strip()
            return int(val) if is_int else val
        except (FileNotFoundError, ValueError):
            return default
            
    energy_now = read_safe("energy_now") or read_safe("charge_now")
    energy_full = read_safe("energy_full") or read_safe("charge_full")
    energy_design = read_safe("energy_full_design") or read_safe("charge_full_design")
    
    health = round((energy_full / energy_design * 100), 1) if energy_design and energy_full else 0
            
    return {
        "capacity":    read_safe("capacity"),
        "status":      read_safe("status", default="Unknown", is_int=False),
        "energy_now":  energy_now,
        "energy_full": energy_full,
        "power_now":   read_safe("power_now"),
        "health":      health
    }
