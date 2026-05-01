<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/b/b8/Lenovo_logo_2015.svg" width="200" alt="Lenovo Logo">
  <h1>Lenovo Legion Toolkit (Linux Edition)</h1>
  <p><b>A robust, native hardware control suite built for Lenovo laptops running on Linux.</b></p>
</div>

---

## Overview

**Lenovo Legion Toolkit (Linux Edition)** is a production-grade unofficial alternative to Lenovo Vantage / Legion Toolkit for GNU/Linux. It brings deep hardware integration to your system, providing you with real-time telemetry, power management, thermal controls, and battery conservation tools directly from a modern GUI. 

Designed natively for Linux, it operates independently of standard OS interfaces by communicating directly with the EC (Embedded Controller) via ACPI/sysfs through a secure, split-privilege D-Bus daemon. 

Whether you run **Wayland** or **X11**, or use **GNOME, KDE Plasma, Cinnamon, or i3**, the toolkit scales natively across high-DPI displays.

---

## Key Features

* **Advanced Power Management:** Quickly toggle between Quiet, Balanced, and Performance thermal profiles (synced directly with the hardware EC and `power-profiles-daemon`).
* **GPU Switching:** Seamlessly manage Hybrid, Integrated, and Dedicated GPU modes via standard `supergfxctl` APIs.
* **Custom TDP Tuning (RyzenAdj):** Override factory hardware power limits (STAPM, Fast, Slow limits in mW) natively from the GUI.
* **Battery Conservation:** Easily toggle Battery Conservation Mode to cap charging at 60-80% to vastly extend battery lifespan, and read deep raw battery analytics.
* **System Hardware Controls:** Configure Always-On USB, Flip-To-Start, Instant-Boot, and Fn-Lock natively.
* **Real-time Telemetry:** Hardware polling engine streams CPU/GPU Utilization, Temperatures, and Fan RPM directly into the Dashboard.
* **Capability Engine:** The GUI auto-adapts to your specific laptop. Missing hardware features (like RGB or specific GPU muxes) are gracefully detected and safely disabled.

---

## Architecture

The project employs a secure split-privilege architecture:
1. `vantaged` (**System Daemon**): Runs as root in the background. Safely executes privileged ACPI, `/sys/class`, and `supergfxctl` hardware calls.
2. `vantage-gui` (**User GUI**): Runs as your standard unprivileged user. A pristine PyQt6 interface that communicates with the daemon exclusively via standard `D-Bus` IPC.

---

## Dependencies

The application relies on core Python libraries and standard hardware packages. Please install the dependencies specific to your Linux Distribution before compiling.

### Debian / Ubuntu / Linux Mint  
```bash
sudo apt update
sudo apt install python3 python3-pip python3-dbus python3-pyqt6 supergfxctl
```

### Fedora / RHEL
```bash
sudo dnf install python3 python3-pip python3-dbus python3-pyqt6 supergfxctl
```

### Arch Linux / Manjaro / EndeavourOS / CachyOS
```bash
sudo pacman -S python python-dbus python-pyqt6 supergfxctl
```

*(Optional)* For advanced CPU tuning on AMD processors, ensure `ryzenadj` is installed in your system `$PATH`.

---

## Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nightcodex7/lenovo-vantage-unofficial-linux.git
   cd lenovo-vantage-unofficial-linux
   ```

2. **Install globally via Makefile:**
   ```bash
   sudo make install
   ```
   *This automatically registers the `lenovo-vantage.service` systemd daemon, enables it, and creates the desktop entries.*

3. **Launch the Application:**
   * Open your application launcher (Super/Windows key) and search for **"Lenovo Vantage"**.
   * Alternatively, you can launch the GUI directly from the terminal:
     ```bash
     vantage-gui
     ```

> **Note on Display Servers:** The GUI explicitly requests Wayland first (`QT_QPA_PLATFORM="wayland;xcb"`) to guarantee flawless high-DPI scaling and crisp text on modern GNOME/KDE Wayland sessions, while perfectly falling back to X11 on legacy environments.

---

## Uninstallation

To completely remove the daemon, application, and clear out `/etc/lenovo-vantage` configuration configs:

```bash
cd lenovo-vantage-unofficial-linux
sudo make uninstall
```

---

## 🤝 Contributing & Support

Contributions are welcome! If you encounter issues mapping specific ACPI commands on your specific Legion/IdeaPad/ThinkBook/other Lenovo devices, please open an Issue.

---

## 🙏 Acknowledgments

A massive thank you to [LenovoLegionToolkit](https://github.com/BartoszCichecki/LenovoLegionToolkit) by Bartosz Cichecki. This project was heavily inspired by and majorly ported from their fantastic work on the Windows equivalent.
