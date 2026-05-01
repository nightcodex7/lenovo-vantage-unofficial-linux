import glob
import subprocess
import os
import shutil

def detect_capabilities() -> dict:
    has_hwmon = len(glob.glob("/sys/class/hwmon/hwmon*")) > 0
    return {
        "supported": has_hwmon,
        "partial": not has_hwmon,
        "reason": "hwmon available" if has_hwmon else "hwmon unavailable"
    }

def read_hwmon(name: str, file: str) -> int | None:
    """Find hwmon by driver name and read a value."""
    for path in glob.glob("/sys/class/hwmon/hwmon*"):
        try:
            with open(f"{path}/name") as f:
                if f.read().strip() == name:
                    with open(f"{path}/{file}") as f_val:
                        return int(f_val.read().strip())
        except (FileNotFoundError, ValueError):
            continue
    return None

def get_cpu_temp() -> float:
    """Returns CPU Tctl/Package temp in °C."""
    raw = read_hwmon("k10temp", "temp1_input")
    if raw is None:
        raw = read_hwmon("coretemp", "temp1_input")
    return raw / 1000.0 if raw else 0.0

def get_gpu_temp() -> float:
    """Returns GPU edge temp in °C, preferring dGPU if available."""
    raw_dgpu = read_hwmon("nouveau", "temp1_input")
    if raw_dgpu:
        return raw_dgpu / 1000.0
    raw_igpu = read_hwmon("amdgpu", "temp1_input")
    return raw_igpu / 1000.0 if raw_igpu else 0.0

def get_cpu_usage() -> float:
    try:
        with open('/proc/loadavg', 'r') as fl:
            load1 = float(fl.read().split()[0])
        num_cores = os.cpu_count() or 1
        usage = (load1 / num_cores) * 100.0
        return min(100.0, usage)
    except Exception:
        return 0.0

def get_gpu_usage() -> float:
    try:
        if shutil.which("nvidia-smi"):
            res = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"], capture_output=True, text=True)
            return float(res.stdout.strip())
    except Exception:
        pass
    return 0.0

def get_fan_rpm() -> int:
    for name in ["ideapad", "thinkpad", "legion", "asus"]:
        raw = read_hwmon(name, "fan1_input")
        if raw is not None:
            return raw
    return 0

