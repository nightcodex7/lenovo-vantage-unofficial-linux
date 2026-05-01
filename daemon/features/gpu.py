import subprocess
import shutil

def detect_capabilities() -> dict:
    if shutil.which("supergfxctl"):
        return {"supported": True, "partial": False, "reason": "supergfxctl available", "tool": "supergfxctl"}
    elif shutil.which("optimus-manager"):
        return {"supported": True, "partial": True, "reason": "optimus-manager available", "tool": "optimus-manager"}
    return {"supported": False, "partial": False, "reason": "No GPU management tool found", "tool": None}

def get_dgpu_mode() -> str:
    caps = detect_capabilities()
    if caps["tool"] == "supergfxctl":
        res = subprocess.run(["supergfxctl", "-g"], capture_output=True, text=True)
        return res.stdout.strip().lower()
    elif caps["tool"] == "optimus-manager":
        res = subprocess.run(["optimus-manager", "--print-mode"], capture_output=True, text=True)
        mode = res.stdout.strip().lower()
        if "hybrid" in mode: return "hybrid"
        if "nvidia" in mode: return "dedicated"
        if "integrated" in mode: return "integrated"
        return "unknown"
    return "disabled"

def set_dgpu_mode(mode: str) -> None:
    caps = detect_capabilities()
    if caps["tool"] == "supergfxctl":
        subprocess.run(["supergfxctl", "-m", mode.capitalize()], check=True)
    elif caps["tool"] == "optimus-manager":
        if mode == "dedicated":
            subprocess.run(["optimus-manager", "--switch", "nvidia"], check=True)
        elif mode == "integrated":
            subprocess.run(["optimus-manager", "--switch", "integrated"], check=True)
        elif mode == "hybrid":
            subprocess.run(["optimus-manager", "--switch", "hybrid"], check=True)
