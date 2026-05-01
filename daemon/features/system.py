import glob
from pathlib import Path

def get_vpc_path():
    vpc_paths = glob.glob("/sys/bus/platform/devices/VPC2004:*")
    return vpc_paths[0] if vpc_paths else None

def detect_capabilities() -> dict:
    vpc = get_vpc_path()
    res = {"fn_lock": False, "flip_to_start": False, "instant_boot": False}
    if vpc:
        if Path(f"{vpc}/fn_lock").exists(): res["fn_lock"] = True
        if Path(f"{vpc}/flip_to_start").exists(): res["flip_to_start"] = True
        if Path(f"{vpc}/instant_boot").exists(): res["instant_boot"] = True
        return {"supported": res["fn_lock"] or res["flip_to_start"], "partial": not all(res.values()), "reason": str(res)}
    return {"supported": False, "partial": False, "reason": "VPC not found"}

def set_fn_lock(enabled: bool) -> None:
    vpc = get_vpc_path()
    if vpc and Path(f"{vpc}/fn_lock").exists(): Path(f"{vpc}/fn_lock").write_text("0" if enabled else "1")

def get_fn_lock() -> bool:
    vpc = get_vpc_path()
    return Path(f"{vpc}/fn_lock").read_text().strip() == "0" if vpc and Path(f"{vpc}/fn_lock").exists() else False

def set_flip_to_start(enabled: bool) -> None:
    vpc = get_vpc_path()
    if vpc and Path(f"{vpc}/flip_to_start").exists(): Path(f"{vpc}/flip_to_start").write_text("1" if enabled else "0")

def get_flip_to_start() -> bool:
    vpc = get_vpc_path()
    return Path(f"{vpc}/flip_to_start").read_text().strip() == "1" if vpc and Path(f"{vpc}/flip_to_start").exists() else False

def set_instant_boot(enabled: bool) -> None:
    vpc = get_vpc_path()
    if vpc and Path(f"{vpc}/instant_boot").exists(): Path(f"{vpc}/instant_boot").write_text("1" if enabled else "0")

def get_instant_boot() -> bool:
    vpc = get_vpc_path()
    return Path(f"{vpc}/instant_boot").read_text().strip() == "1" if vpc and Path(f"{vpc}/instant_boot").exists() else False
