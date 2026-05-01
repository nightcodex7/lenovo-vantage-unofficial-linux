import os
import subprocess
import shutil
from pathlib import Path

PROFILE_MAP = {
    "quiet":       "low-power",
    "balanced":    "balanced",
    "performance": "performance",
}

PLATFORM_PROFILE = "/sys/firmware/acpi/platform_profile"

def detect_capabilities() -> dict:
    has_sysfs = Path(PLATFORM_PROFILE).exists()
    has_ppd = shutil.which("powerprofilesctl") is not None
    if has_sysfs and has_ppd:
        return {"supported": True, "partial": False, "reason": "Hardware and OS profiles available"}
    elif has_sysfs or has_ppd:
        return {"supported": True, "partial": True, "reason": "Only one layer of power control available"}
    return {"supported": False, "partial": False, "reason": "No power control available"}

def set_power_mode(mode: str) -> None:
    """Map LLT power mode names to Linux platform_profile and sync with power-profiles-daemon."""
    profile = PROFILE_MAP.get(mode.lower())
    if not profile:
        raise ValueError(f"Unknown mode: {mode}")
    
    try:
        if Path(PLATFORM_PROFILE).exists():
            Path(PLATFORM_PROFILE).write_text(profile)
    except Exception:
        pass
        
    if shutil.which("powerprofilesctl"):
        try:
            ppd_mode = "power-saver" if profile == "low-power" else profile
            subprocess.run(["powerprofilesctl", "set", ppd_mode], check=True)
        except Exception:
            pass

def get_power_mode() -> str:
    try:
        if Path(PLATFORM_PROFILE).exists():
            raw = Path(PLATFORM_PROFILE).read_text().strip()
            rev = {v: k for k, v in PROFILE_MAP.items()}
            return rev.get(raw, raw).capitalize()
        elif shutil.which("powerprofilesctl"):
            res = subprocess.run(["powerprofilesctl", "get"], capture_output=True, text=True)
            raw = res.stdout.strip()
            if raw == "power-saver": raw = "low-power"
            rev = {v: k for k, v in PROFILE_MAP.items()}
            return rev.get(raw, raw).capitalize()
        return "Unknown"
    except Exception:
        return "Unknown"

def set_ryzen_tdp(stapm_limit_mw: int, fast_limit_mw: int, slow_limit_mw: int) -> bool:
    if not shutil.which("ryzenadj"):
        return False
    try:
        subprocess.run([
            "ryzenadj",
            f"--stapm-limit={stapm_limit_mw}",
            f"--fast-limit={fast_limit_mw}",
            f"--slow-limit={slow_limit_mw}",
        ], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def get_ryzen_tdp() -> dict:
    if not shutil.which("ryzenadj"):
        return {"stapm": 45000, "fast": 45000, "slow": 45000, "supported": False}
    try:
        res = subprocess.run(["ryzenadj", "-i"], check=True, capture_output=True, text=True)
        out = res.stdout.upper()
        
        def extract_limit(key, default):
            for line in out.splitlines():
                if key in line:
                    import re
                    match = re.search(r'[\d\.]+', line.replace(',', '.'))
                    if match:
                        val = float(match.group())
                        # If it's in Watts (e.g. 45.000), convert to mW. Otherwise assume mW.
                        if val < 200:
                            return int(val * 1000)
                        return int(val)
            return default
            
        return {
            "stapm": extract_limit("STAPM", 45000),
            "fast": extract_limit("FAST", 45000),
            "slow": extract_limit("SLOW", 45000),
            "supported": True
        }
    except Exception:
        return {"stapm": 45000, "fast": 45000, "slow": 45000, "supported": False}
