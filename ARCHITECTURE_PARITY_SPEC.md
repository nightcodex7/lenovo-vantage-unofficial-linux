# Lenovo Vantage Linux – Universal Feature Parity & Implementation Specification

## 0. Purpose
This document defines a **complete, production-grade specification** to achieve feature parity with the Windows Lenovo Legion Toolkit (LLT), while implementing a **Linux-native, hardware-aware, and extensible system**.

This is NOT a translation effort. This is a **hardware abstraction + re-engineering effort**.

---

## 1. Design Principles

1. **Linux-native first**: Use `sysfs`, ACPI, kernel interfaces. Avoid Windows abstractions.
2. **Hardware-aware dynamic behavior**: NEVER assume feature availability. Detect capabilities at runtime.
3. **Graceful degradation**: 
   - Unsupported features → Greyed out
   - Partially supported features → Warning icon + limited UI
4. **Modular + extensible**: Works across IdeaPad Gaming, Legion series, ThinkBook, and future Lenovo devices.
5. **Cross-distro compatibility**: Fedora, Ubuntu, Arch, Debian, openSUSE.

---

## 2. Architecture Overview

### 2.1 Core Components

| Component | Role |
|-----------|------|
| `vantaged` | Root daemon (systemd + D-Bus) |
| `vantage-cli` | CLI interface |
| `vantage-gui` | PyQt6 GUI |
| `feature modules` | Hardware-specific implementations |

### 2.2 Feature Abstraction Layer (MANDATORY)

All hardware features must be accessed via abstraction:

```python
class Feature:
    def is_supported() -> bool
    def get_state()
    def set_state(value)
    def detect_capabilities() -> dict
```

---

## 3. Feature Matrix (Windows → Linux Mapping)

### 3.1 Power Management
| Windows | Linux Implementation | Requirements | UI Behavior |
|---------|-----------------------|--------------|-------------|
| WMI EC control | Primary: `/sys/firmware/acpi/platform_profile`<br>Secondary: `power-profiles-daemon` | Sync hardware profile and OS power profile. | **Supported**: Normal<br>**Missing sysfs**: Greyed<br>**Partial**: Warning icon |

### 3.2 Fan Control
| Linux Sources | Modes | Constraints | UI Rules |
|---------------|-------|-------------|----------|
| `/sys/bus/platform/devices/VPC2004:*/fan_mode`<br>`/sys/class/hwmon/*` | Silent, Standard, Performance, Dust Cleaning, PWM control (optional) | Many devices lock EC (read-only). Cannot override curves. | **Writable PWM**: Enable curve<br>**Read-only**: Disable curve<br>**No access**: Greyed out |

### 3.3 Battery Features
| Features | Linux Paths | UI Logic |
|----------|-------------|----------|
| Conservation mode, Charge threshold, Battery health | `/sys/class/power_supply/BAT*/charge_control_end_threshold`<br>`/sys/bus/platform/devices/VPC2004:*/conservation_mode` | If threshold exists → Show slider<br>Else → Hide slider |

### 3.4 GPU Management
| Linux Implementation | Modes | UI Rules |
|-----------------------|-------|----------|
| Priority: `supergfxctl` → `optimus-manager` → `nvidia-smi` | Hybrid, Integrated, Dedicated | **supergfxctl**: Full support<br>**optimus-manager**: Limited<br>**None**: Greyed out |

*(Note: DO NOT USE `modprobe -r nouveau` blindly).*

### 3.5 RGB / Keyboard Lighting
| Tools | Detection | UI Rules |
|-------|-----------|----------|
| `OpenRGB`, Vendor tools | `openrgb --list-devices` | **Supported**: Full<br>**Partial zones**: Partial UI<br>**Not supported**: Greyed out |

### 3.6 Sensors & Monitoring
| Sources | Metrics |
|---------|---------|
| `/sys/class/hwmon`, `/proc/stat`, `nvidia-smi` | CPU/GPU usage, Temps, Clocks, Fan RPM |

### 3.7 Automation Engine (CRITICAL FEATURE)
| Trigger | Implementation | Example Action |
|---------|----------------|----------------|
| AC plug events | `udevadm` / sysfs polling | `on_ac_connect`: Set `performance` & `dedicated` GPU |
| Battery changes | sysfs polling | `on_battery_low`: Set `quiet` & `integrated` GPU |

### 3.8 Fn Key / Hotkeys
| Detection | Behavior |
|-----------|----------|
| `acpi_listen` / ACPI module | Map Fn+Q → Power mode cycle. Allow custom overrides via Automation Engine. |

### 3.9 Overclocking
| Component | Linux Tool | UI Rules |
|-----------|------------|----------|
| **CPU** | `ryzenadj` | **Available**: Enabled |
| **GPU** | `nvidia-settings` (limited) | **Wayland**: Warning<br>**Not available**: Greyed out |

### 3.10 Unsupported / Unsafe Features
| Feature | Status |
|---------|--------|
| Boot logo flashing | **NOT IMPLEMENTED** |
| BIOS-level GPU switching | **NOT POSSIBLE** |
| Full EC fan curve override | **Device-dependent** |

---

## 4. Capability Detection System (MANDATORY)

Every feature module (`power.py`, `fan.py`, `gpu.py`, etc.) must implement:

```python
def detect_capabilities() -> dict:
    return {
        "supported": bool,
        "partial": bool,
        "reason": str
    }
```

---

## 5. UI/UX Behavior Rules

### 5.1 Feature States
| State | UI Behavior |
|-------|-------------|
| **Supported** | Enabled |
| **Partial** | Enabled + Warning Icon / Tooltip |
| **Unsupported** | Greyed out + Reason Tooltip |

### 5.2 Warning Examples
- "Your device firmware does not allow this feature."
- "This feature requires NVIDIA proprietary drivers."
- "Wayland limits GPU overclocking."

### 5.3 Dynamic UI Rendering
The UI must adapt at runtime by fetching `GetAllCapabilities` from the daemon. It hides irrelevant features, disables unsupported toggles, and shows contextual tooltips automatically.

---

## 6. Cross-Distro Support
**Must Support:** Fedora (`dnf`), Ubuntu/Debian (`apt`), Arch (`pacman`), openSUSE (`zypper`).
**Installer Requirements:** Auto-detect distro, install dependencies (`python3-dbus`, `PyQt6`, `zenity`, `xinput`), validate kernel modules.

---

## 7. Hardware Compatibility Strategy
| Device Type | Strategy |
|-------------|----------|
| **Legion** | Full support |
| **IdeaPad Gaming** | Partial support |
| **ThinkBook** | Limited support |
| **Unknown** | Detection-first (Graceful degradation) |

---

## 8. Logging & Debugging
All actions logged. Include: `sysfs` writes, command outputs, and errors via `systemd` journal.

---

## 9. Testing Requirements
Must validate:
1. Feature detection accuracy on mismatched hardware.
2. No crashes on unsupported systems.
3. Proper UI degradation dynamically.

---

## 10. Extensions
- **CLI scripting support** via `vantage-cli`.
- **Profiles** (Automation engine support).
- **Wayland-native design** (PyQt6 native).
- **Modular Plugin architecture** (daemon feature modules).
