import glob
from pathlib import Path

def get_vpc_path():
    vpc_paths = glob.glob("/sys/bus/platform/devices/VPC2004:*")
    return vpc_paths[0] if vpc_paths else None

def detect_capabilities() -> dict:
    vpc = get_vpc_path()
    if vpc and Path(f"{vpc}/fan_mode").exists():
        return {"supported": True, "partial": False, "reason": "VPC fan_mode available"}
    return {"supported": False, "partial": False, "reason": "No fan control available"}

FAN_MODES = {
    "super_silent": 0,
    "standard":     1,
    "dust_cleaning":   2,
    "performance":  4,
}

def set_fan_mode(mode: str) -> None:
    vpc = get_vpc_path()
    if not vpc:
        raise FileNotFoundError("VPC device not found")
        
    val = FAN_MODES.get(mode.lower().replace(" ", "_"))
    if val is None:
        raise ValueError(f"Unknown fan mode: {mode}")
    Path(f"{vpc}/fan_mode").write_text(str(val))

def get_fan_mode() -> str:
    vpc = get_vpc_path()
    if not vpc:
        return "Unknown"
    try:
        raw = int(Path(f"{vpc}/fan_mode").read_text().strip())
        raw = 0 if raw == 133 else raw
        rev = {v: k.replace("_", " ").title() for k, v in FAN_MODES.items()}
        return rev.get(raw, "Unknown")
    except FileNotFoundError:
        return "Unknown"
