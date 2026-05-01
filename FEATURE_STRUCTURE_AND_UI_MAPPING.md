# Lenovo Vantage Linux – Feature Structure & UI Mapping (Aligned Specification)

## 0. Objective

Define an **accurate, implementation-aligned UI + feature structure** based on:

- Current Linux implementation (README + architecture)
- Windows Lenovo Legion Toolkit UI (reference screenshots)
- Parity specification (ARCHITECTURE_PARITY_SPEC.md)

This document ensures:
- No fake features
- No unsupported assumptions
- Full alignment with daemon + feature modules
- Correct capability-aware UI behavior

---

# 1. GLOBAL NAVIGATION STRUCTURE

## Tabs (Strict Order)

1. Dashboard
2. Power
3. Battery
4. Actions
5. Settings
6. About
7. Donate

❌ Not implemented (do NOT include unless built):
- Macro
- Downloads

---

# 2. DASHBOARD TAB

## Purpose
Real-time monitoring + quick controls

## Sections

### 2.1 System Monitoring (READ-ONLY)
- CPU usage
- CPU temperature
- GPU usage
- GPU temperature
- Fan RPM
- Battery %

### Backend
- `/sys/class/hwmon`
- `/proc/stat`
- `nvidia-smi`

---

### 2.2 Quick Controls (WRITE)

#### Power Mode
- quiet / balanced / performance

#### GPU Mode
- hybrid / integrated / dedicated

#### Fan Mode
- silent / standard / performance / dust

---

### UI Behavior
- If feature unsupported → hide or grey
- Always reflect real hardware state (no assumptions)

---

# 3. POWER TAB

## Purpose
Primary hardware control center

---

## 3.1 Power Mode

### Features
- Quiet / Balanced / Performance
- Fn+Q sync (if detectable)

### Backend
- `/sys/firmware/acpi/platform_profile`
- `power-profiles-daemon`

---

## 3.2 Battery Mode

### Features
- Conservation Mode

### Backend
- `/sys/bus/platform/devices/VPC2004:*/conservation_mode`

---

## 3.3 Always-On USB

### Backend
- VPC2004 `usb_charging`

---

## 3.4 Flip To Start

⚠️ Only if supported by ACPI  
Else → greyed out

---

## 3.5 GPU SECTION

### GPU Working Mode
- Hybrid
- Integrated
- Dedicated

### Backend Priority
1. `supergfxctl`
2. `optimus-manager`
3. fallback: none

---

### Discrete GPU Toggle
- Enable / Disable dGPU

---

### GPU Overclock

### Backend
- `nvidia-settings`

### UI Rules
- Wayland → warning
- Missing NVIDIA → greyed

---

## 3.6 THERMAL / FAN CONTROL

### Modes
- Super Silent
- Standard
- Performance
- Dust Cleaning

### Backend
- `/sys/bus/platform/devices/VPC2004:*/fan_mode`

---

### Advanced Fan Curve (ONLY IF AVAILABLE)

- PWM control via `/sys/class/hwmon`

---

## 3.7 DISPLAY SECTION

### Features
- Resolution
- Scaling (DPI)
- Turn off display

### Backend
- `xrandr` (X11)
- Wayland APIs (limited)

---

## 3.8 SYSTEM CONTROLS

### Keyboard Backlight
- Basic toggle / levels

### Backend
- OpenRGB (if detected)

---

### Touchpad Toggle
- enable / disable

### Backend
- `xinput` / libinput

---

### Fn Lock
- toggle Fn behavior

### Backend
- VPC2004 `fn_lock`

---

### Windows Key Lock

⚠️ Only if supported  
Else → greyed

---

# 4. BATTERY TAB

## Purpose
Detailed analytics (READ-ONLY)

---

## Features

- Battery %
- Charging state
- Temperature
- Discharge rate
- Current capacity
- Full capacity
- Design capacity
- Cycle count
- Health %

---

## Backend
- `/sys/class/power_supply/`

---

# 5. ACTIONS TAB (AUTOMATION ENGINE)

## Purpose
Event-driven automation (CORE FEATURE)

---

## 5.1 Master Toggle
- Enable / Disable automation

---

## 5.2 Triggers

### Implemented
- AC Connected
- AC Disconnected

### Extendable
- Battery level
- App launch

---

## 5.3 Actions

- Set Power Mode
- Set GPU Mode
- Set Fan Mode
- Run script
- Kill process

---

## 5.4 Quick Actions

- One-click execution
- Tray integration

---

## Backend
- systemd daemon
- udev events
- polling engine

---

# 6. SETTINGS TAB

---

## 6.1 General

- Language
- Temperature unit (°C / °F)
- Theme (Light/Dark/System)
- Accent color

---

## 6.2 Behavior

- Autorun
- Minimize to tray
- Close behavior

---

## 6.3 Power Integration

### Power Mode Sync
- Sync hardware + OS profile

---

## 6.4 Advanced

### Smart Fn Lock
- Conditional Fn behavior

---

### Single Brightness Sync
- Sync brightness across profiles

---

## 6.5 Boot Logo

❌ NOT IMPLEMENTED  
→ Always greyed

---

## 6.6 Updates

- Check updates
- Auto update frequency

---

## 6.7 Integrations

- Enable CLI
- Add CLI to PATH

---

# 7. ABOUT TAB

- Version
- Build
- Dependencies
- Links

---

# 8. DONATE TAB

- Static UI

---

# 9. CAPABILITY-AWARE UI ENGINE (MANDATORY)

Every feature MUST expose:

```python
{
  "supported": bool,
  "partial": bool,
  "reason": str
}

---

# UI STATE RULES
Supported
Fully enabled
Partial
Enabled + warning icon
Unsupported
Greyed out + tooltip

---

# 9.1 EXAMPLES

| Case                        | UI                           |
| --------------------------- | ---------------------------- |
| No NVIDIA GPU               | GPU controls disabled        |
| Wayland                     | GPU OC warning               |
| No OpenRGB                  | RGB hidden                   |
| No VPC2004 (other)          | fan + fn features disabled   |

---

# 10. STRICT IMPLEMENTATION CONSTRAINTS
NO hardcoded sysfs paths
NO fake features
NO Windows API assumptions
ALWAYS runtime detection
MUST not crash on unsupported hardware