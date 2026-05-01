#!/usr/bin/env python3
import sys
import os
import dbus
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QSpinBox, QMessageBox, 
                             QGridLayout, QComboBox, QProgressBar, QFrame, QScrollArea, 
                             QStackedWidget, QButtonGroup)
from PyQt6.QtGui import QIcon, QFont, QCursor
from PyQt6.QtCore import QTimer, Qt

DARK_STYLESHEET = """
QMainWindow, QWidget#MainWidget, QScrollArea, QStackedWidget, QWidget#ScrollContent {
    background-color: #121212;
    color: #e0e0e0;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    border: none;
}
QToolTip {
    background-color: #1e1e1e;
    color: #e0e0e0;
    border: 1px solid #333333;
    border-radius: 4px;
    padding: 6px;
    font-size: 12px;
}
QWidget#Sidebar {
    background-color: #181818;
    border-right: 1px solid #222222;
}
QPushButton.SidebarBtn {
    background-color: transparent;
    color: #9e9e9e;
    text-align: left;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: 600;
    border: none;
    border-radius: 6px;
    margin: 2px 10px;
}
QPushButton.SidebarBtn:hover:!checked {
    background-color: #242424;
    color: #ffffff;
}
QPushButton.SidebarBtn:checked {
    background-color: #2a2a2a;
    color: #ffffff;
    border-left: 3px solid #0078d4;
    border-top-left-radius: 0px;
    border-bottom-left-radius: 0px;
}
QFrame#SettingsRow, QFrame#DashboardCard {
    background-color: #1e1e1e;
    border: 1px solid #2a2a2a;
    border-radius: 8px;
}
QFrame#SettingsRow:disabled {
    background-color: #181818;
    border: 1px solid #222222;
}
QLabel {
    color: #e0e0e0;
}
QLabel#RowTitle {
    font-weight: 600;
    font-size: 14px;
    color: #ffffff;
}
QFrame#SettingsRow:disabled QLabel#RowTitle {
    color: #666666;
}
QLabel#RowSubtitle {
    color: #aaaaaa;
    font-size: 12px;
}
QFrame#SettingsRow:disabled QLabel#RowSubtitle {
    color: #444444;
}
QLabel#SectionTitle {
    font-size: 16px;
    font-weight: bold;
    color: #ffffff;
    margin-top: 25px;
    margin-bottom: 8px;
}
QLabel#PageTitle {
    font-size: 26px;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 10px;
}
QComboBox, QSpinBox {
    background-color: #2a2a2a;
    border: 1px solid #3a3a3a;
    border-radius: 6px;
    padding: 6px 12px;
    color: #ffffff;
    min-width: 140px;
    font-size: 13px;
    font-weight: 500;
}
QComboBox:disabled, QSpinBox:disabled {
    background-color: #1a1a1a;
    color: #555555;
    border: 1px solid #222222;
}
QComboBox:hover:!disabled, QSpinBox:hover:!disabled {
    background-color: #333333;
    border: 1px solid #4a4a4a;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 32px;
    border-left: 1px solid #333333;
}
QComboBox::down-arrow {
    image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAQUlEQVR4nGNgGAWDFKxateo/seJMuBShK8YljmFAWFgYIz5NyPIMDAwMjAw4ADbnomvG6gJcirFpJgrgCtBRgAAAIvoi+TgJKhgAAAAASUVORK5CYII=");
    width: 16px;
    height: 16px;
}
QComboBox::down-arrow:disabled {
    image: url("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAQUlEQVR4nGNgGAWDFISGhv4nVpwJlyJ0xbjEMQxYvXo1Iz5NyPIMDAwMjAw4ADbnomvG6gJcirFpJgrgCtBRgAAAUyEd/s1WBOUAAAAASUVORK5CYII=");
}
QPushButton#ApplyBtn {
    background-color: #0078d4;
    color: white;
    font-weight: 600;
    font-size: 13px;
    border-radius: 6px;
    padding: 8px 16px;
}
QPushButton#ApplyBtn:hover:!disabled {
    background-color: #106ebe;
}
QPushButton#ApplyBtn:disabled {
    background-color: #333333;
    color: #777777;
}
QProgressBar {
    background-color: #2a2a2a;
    border: none;
    border-radius: 4px;
    text-align: right;
    color: transparent;
}
QProgressBar::chunk {
    background-color: #d83b01;
    border-radius: 4px;
}
QScrollBar:vertical {
    border: none;
    background: #121212;
    width: 10px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #333333;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

def get_battery_info():
    info = {"percent": "N/A", "status": "N/A", "health": "N/A", "cycles": "N/A", "current": "N/A", "full": "N/A", "design": "N/A"}
    for bat in os.listdir("/sys/class/power_supply/"):
        if bat.startswith("BAT"):
            path = f"/sys/class/power_supply/{bat}"
            try:
                if os.path.exists(f"{path}/capacity"): info["percent"] = open(f"{path}/capacity").read().strip()
                if os.path.exists(f"{path}/status"): info["status"] = open(f"{path}/status").read().strip()
                
                en_now = "energy_now" if os.path.exists(f"{path}/energy_now") else "charge_now"
                en_full = "energy_full" if os.path.exists(f"{path}/energy_full") else "charge_full"
                en_des = "energy_full_design" if os.path.exists(f"{path}/energy_full_design") else "charge_full_design"
                
                if os.path.exists(f"{path}/{en_now}"): info["current"] = open(f"{path}/{en_now}").read().strip()
                if os.path.exists(f"{path}/{en_full}"): info["full"] = open(f"{path}/{en_full}").read().strip()
                if os.path.exists(f"{path}/{en_des}"): info["design"] = open(f"{path}/{en_des}").read().strip()
                if os.path.exists(f"{path}/cycle_count"): info["cycles"] = open(f"{path}/cycle_count").read().strip()
                
                if info["full"] != "N/A" and info["design"] != "N/A":
                    info["health"] = f"{(float(info['full']) / float(info['design'])) * 100:.1f}%"
            except: pass
            break
    return info

def get_laptop_model():
    try:
        with open("/sys/class/dmi/id/product_version") as f:
            val = f.read().strip()
            if val and val.lower() != "lenovo" and val != "None":
                return val
    except: pass
    try:
        with open("/sys/class/dmi/id/product_name") as f:
            name = f.read().strip()
        try:
            with open("/sys/class/dmi/id/product_family") as f:
                family = f.read().strip()
            if family and family.lower() != "lenovo":
                return f"{family} ({name})"
        except: pass
        return name
    except:
        return "Unknown Lenovo Device"

class VantageService:
    def __init__(self):
        try:
            bus = dbus.SystemBus()
            obj = bus.get_object("org.lenovo.Vantage", "/org/lenovo/Vantage")
            self.iface = dbus.Interface(obj, "org.lenovo.Vantage")
        except dbus.exceptions.DBusException as e:
            raise Exception("Daemon not running or accessible") from e

class VantageGUI(QMainWindow):
    def __init__(self, svc):
        super().__init__()
        self.svc = svc
        self.setWindowTitle("Lenovo Legion Toolkit (Linux Edition)")
        self.resize(1000, 750)
        self.setStyleSheet(DARK_STYLESHEET)
        
        # UI Element Tracking for easy updates
        self.pm_combos = []
        self.gpu_combos = []
        self.fan_combos = []
        
        self.bat_combos = []
        self.usb_combos = []
        self.ib_combos = []
        self.fs_combos = []
        self.fn_combos = []
        
        self.tdp_spins = []
        self.rows = {} 
        
        main_widget = QWidget()
        main_widget.setObjectName("MainWidget")
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        self.setCentralWidget(main_widget)
        
        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(220)
        side_layout = QVBoxLayout(self.sidebar)
        side_layout.setContentsMargins(0, 20, 0, 20)
        side_layout.setSpacing(5)
        
        title_lbl = QLabel(" Legion Toolkit")
        title_lbl.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-left: 15px; margin-bottom: 20px;")
        side_layout.addWidget(title_lbl)
        
        self.nav_btns = []
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)
        
        # "Donate" removed from UI entirely as requested
        tabs = ["Dashboard", "Power", "Battery", "Actions", "Settings", "About"]
        for idx, t in enumerate(tabs):
            if t == "About":
                side_layout.addStretch() # Push About to the very bottom
                
            btn = QPushButton(t)
            btn.setProperty("class", "SidebarBtn")
            btn.setCheckable(True)
            self.btn_group.addButton(btn, idx)
            btn.clicked.connect(lambda checked, i=idx: self.switch_tab(i))
            side_layout.addWidget(btn)
            self.nav_btns.append(btn)
            
        main_layout.addWidget(self.sidebar)
        
        # Stacked Widget
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # Pages
        self.stack.addWidget(self.create_dashboard_page())
        self.stack.addWidget(self.create_power_page())
        self.stack.addWidget(self.create_battery_page())
        self.stack.addWidget(self.create_actions_page())
        self.stack.addWidget(self.create_settings_page())
        self.stack.addWidget(self.create_about_page())
        
        self.switch_tab(0) # Select Dashboard
        self.load_state()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_sensors)
        self.timer.start(2000)
        self.update_sensors()

    def switch_tab(self, idx):
        self.nav_btns[idx].setChecked(True)
        self.stack.setCurrentIndex(idx)

    def _make_info_icon(self, tooltip_text):
        lbl = QLabel("ⓘ")
        lbl.setStyleSheet("color: #888888; font-size: 16px; font-weight: bold;")
        lbl.setToolTip(tooltip_text)
        lbl.setCursor(QCursor(Qt.CursorShape.WhatsThisCursor))
        return lbl

    def _create_row(self, title, subtitle, widget, tooltip="", obj_name="SettingsRow"):
        row = QFrame()
        row.setObjectName(obj_name)
        h = QHBoxLayout(row)
        h.setContentsMargins(20, 15, 20, 15)
        
        text_v = QVBoxLayout()
        text_v.setSpacing(4)
        lbl_title = QLabel(title)
        lbl_title.setObjectName("RowTitle")
        text_v.addWidget(lbl_title)
        
        if subtitle:
            lbl_sub = QLabel(subtitle)
            lbl_sub.setObjectName("RowSubtitle")
            lbl_sub.setWordWrap(True)
            text_v.addWidget(lbl_sub)
        
        h.addLayout(text_v)
        h.addStretch()
        
        if tooltip:
            h.addWidget(self._make_info_icon(tooltip))
            h.addSpacing(10)
        if widget:
            h.addWidget(widget)
        
        return row

    def _create_scroll_page(self, title):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        layout.addWidget(scroll)
        
        content = QWidget()
        content.setObjectName("ScrollContent")
        scroll.setWidget(content)
        
        clayout = QVBoxLayout(content)
        clayout.setContentsMargins(40, 30, 40, 40)
        clayout.setSpacing(15)
        
        lbl = QLabel(title)
        lbl.setObjectName("PageTitle")
        clayout.addWidget(lbl)
        
        return page, clayout

    # --- TABS ---

    def create_dashboard_page(self):
        page, layout = self._create_scroll_page("Dashboard")
        
        lbl_model = QLabel(get_laptop_model())
        lbl_model.setStyleSheet("font-size: 16px; color: #aaaaaa; padding-bottom: 10px;")
        layout.addWidget(lbl_model)
        
        # System Monitoring
        dash_group = QFrame()
        dash_group.setObjectName("DashboardCard")
        dash_layout = QHBoxLayout(dash_group)
        dash_layout.setContentsMargins(25, 25, 25, 25)
        dash_layout.setSpacing(40)
        
        # CPU
        cpu_w = QWidget()
        cpu_l = QGridLayout(cpu_w)
        cpu_l.setContentsMargins(0, 0, 0, 0)
        cpu_l.setVerticalSpacing(18)
        cpu_title = QLabel("CPU")
        cpu_title.setStyleSheet("font-weight: bold; font-size: 18px; color: #ffffff;")
        cpu_l.addWidget(cpu_title, 0, 0, 1, 3)
        
        cpu_l.addWidget(QLabel("Utilization"), 1, 0)
        self.pb_cpu = QProgressBar()
        self.pb_cpu.setFixedHeight(8)
        self.pb_cpu.setRange(0, 100)
        cpu_l.addWidget(self.pb_cpu, 1, 1)
        self.lbl_cpu_util = QLabel("0.0%")
        self.lbl_cpu_util.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        cpu_l.addWidget(self.lbl_cpu_util, 1, 2)
        
        cpu_l.addWidget(QLabel("Temperature"), 2, 0)
        self.pb_cput = QProgressBar()
        self.pb_cput.setFixedHeight(8)
        self.pb_cput.setRange(0, 100)
        cpu_l.addWidget(self.pb_cput, 2, 1)
        self.lbl_cpu_temp = QLabel("0.0 °C")
        self.lbl_cpu_temp.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        cpu_l.addWidget(self.lbl_cpu_temp, 2, 2)
        
        cpu_l.addWidget(QLabel("Fan"), 3, 0)
        self.pb_cpuf = QProgressBar()
        self.pb_cpuf.setFixedHeight(8)
        self.pb_cpuf.setRange(0, 5000)
        cpu_l.addWidget(self.pb_cpuf, 3, 1)
        self.lbl_cpu_fan = QLabel("0 RPM")
        self.lbl_cpu_fan.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        cpu_l.addWidget(self.lbl_cpu_fan, 3, 2)
        
        dash_layout.addWidget(cpu_w)
        
        # GPU
        gpu_w = QWidget()
        gpu_l = QGridLayout(gpu_w)
        gpu_l.setContentsMargins(0, 0, 0, 0)
        gpu_l.setVerticalSpacing(18)
        gpu_title = QLabel("GPU")
        gpu_title.setStyleSheet("font-weight: bold; font-size: 18px; color: #ffffff;")
        gpu_l.addWidget(gpu_title, 0, 0, 1, 3)
        
        gpu_l.addWidget(QLabel("Utilization"), 1, 0)
        self.pb_gpu = QProgressBar()
        self.pb_gpu.setFixedHeight(8)
        self.pb_gpu.setRange(0, 100)
        gpu_l.addWidget(self.pb_gpu, 1, 1)
        self.lbl_gpu_util = QLabel("0.0%")
        self.lbl_gpu_util.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        gpu_l.addWidget(self.lbl_gpu_util, 1, 2)
        
        gpu_l.addWidget(QLabel("Temperature"), 2, 0)
        self.pb_gput = QProgressBar()
        self.pb_gput.setFixedHeight(8)
        self.pb_gput.setRange(0, 100)
        gpu_l.addWidget(self.pb_gput, 2, 1)
        self.lbl_gpu_temp = QLabel("0.0 °C")
        self.lbl_gpu_temp.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        gpu_l.addWidget(self.lbl_gpu_temp, 2, 2)
        
        gpu_l.addWidget(QLabel("Fan"), 3, 0)
        self.pb_gpuf = QProgressBar()
        self.pb_gpuf.setFixedHeight(8)
        self.pb_gpuf.setRange(0, 5000)
        gpu_l.addWidget(self.pb_gpuf, 3, 1)
        self.lbl_gpu_fan = QLabel("N/A")
        self.lbl_gpu_fan.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        gpu_l.addWidget(self.lbl_gpu_fan, 3, 2)
        
        dash_layout.addWidget(gpu_w)
        layout.addWidget(dash_group)
        
        # Quick Controls
        lbl_qc = QLabel("Quick Controls")
        lbl_qc.setObjectName("SectionTitle")
        layout.addWidget(lbl_qc)
        
        pm = QComboBox()
        pm.addItems(["Quiet", "Balance", "Performance"])
        self.pm_combos.append(pm)
        pm.currentIndexChanged.connect(self.auto_apply_change)
        self.rows['power_dash'] = self._create_row("Power Mode", "Change current performance mode.", pm)
        layout.addWidget(self.rows['power_dash'])
        
        gm = QComboBox()
        gm.addItems(["Hybrid", "Integrated", "Dedicated"])
        self.gpu_combos.append(gm)
        gm.currentIndexChanged.connect(self.auto_apply_change)
        self.rows['gpu_dash'] = self._create_row("GPU Working Mode", "Switch between hybrid, integrated, or dedicated.", gm)
        layout.addWidget(self.rows['gpu_dash'])
        
        fm = QComboBox()
        fm.addItems(["Standard", "Super Silent", "Dust Cleaning", "Performance"])
        self.fan_combos.append(fm)
        fm.currentIndexChanged.connect(self.auto_apply_change)
        self.rows['fan_dash'] = self._create_row("Active Cooling Policy", "Control EC fan curve behavior.", fm)
        layout.addWidget(self.rows['fan_dash'])
        
        layout.addStretch()
        return page

    def create_power_page(self):
        page, layout = self._create_scroll_page("Power & System")
        
        lbl_pwr = QLabel("Power")
        lbl_pwr.setObjectName("SectionTitle")
        layout.addWidget(lbl_pwr)
        
        pm = QComboBox()
        pm.addItems(["Quiet", "Balance", "Performance"])
        self.pm_combos.append(pm)
        pm.currentIndexChanged.connect(self.auto_apply_change)
        self.rows['power_main'] = self._create_row("Power Mode", "Change performance mode. Can also be changed with Fn+Q.", pm)
        layout.addWidget(self.rows['power_main'])
        
        bat = QComboBox()
        bat.addItems(["Normal", "Conservation"])
        self.bat_combos.append(bat)
        bat.currentIndexChanged.connect(self.auto_apply_change)
        self.rows['battery'] = self._create_row("Battery Mode", "Conservation mode limits charge to extend battery lifespan.", bat)
        layout.addWidget(self.rows['battery'])
        
        usb = QComboBox()
        usb.addItems(["Off", "On"])
        self.usb_combos.append(usb)
        usb.currentIndexChanged.connect(self.auto_apply_change)
        self.rows['usb'] = self._create_row("Always on USB", "Charge USB devices when the laptop is off.", usb)
        layout.addWidget(self.rows['usb'])

        ib = QComboBox()
        ib.addItems(["Off", "On"])
        self.ib_combos.append(ib)
        ib.currentIndexChanged.connect(self.auto_apply_change)
        self.rows['ib'] = self._create_row("Instant Boot", "Turn on the laptop when a charger is connected.", ib)
        layout.addWidget(self.rows['ib'])
        
        fs = QComboBox()
        fs.addItems(["Off", "On"])
        self.fs_combos.append(fs)
        fs.currentIndexChanged.connect(self.auto_apply_change)
        self.rows['fs'] = self._create_row("Flip To Start", "Turn on the laptop when you open the lid.", fs)
        layout.addWidget(self.rows['fs'])
        
        # GPU Section
        lbl_gpu = QLabel("GPU Section")
        lbl_gpu.setObjectName("SectionTitle")
        layout.addWidget(lbl_gpu)
        
        gm = QComboBox()
        gm.addItems(["Hybrid", "Integrated", "Dedicated"])
        self.gpu_combos.append(gm)
        gm.currentIndexChanged.connect(self.auto_apply_change)
        self.rows['gpu_main'] = self._create_row("GPU Working Mode", "Select GPU operating mode. Switching modes may require restart.", gm, "Uses supergfxctl to set GPU mode.")
        layout.addWidget(self.rows['gpu_main'])
        
        dt = QComboBox()
        dt.addItems(["Disabled"])
        dt.setEnabled(False)
        dt_row = self._create_row("Discrete GPU Toggle", "Not available.", dt, "Unsupported on this architecture.")
        dt_row.setEnabled(False)
        layout.addWidget(dt_row)
        
        oc = QComboBox()
        oc.addItems(["Disabled"])
        oc.setEnabled(False)
        oc_row = self._create_row("GPU Overclock", "Not currently available.", oc, "Missing NVIDIA Coolbits or unsupported setup.")
        oc_row.setEnabled(False)
        layout.addWidget(oc_row)
        
        # Thermal / Fan
        lbl_fan = QLabel("Thermal / Fan Control")
        lbl_fan.setObjectName("SectionTitle")
        layout.addWidget(lbl_fan)
        
        fm = QComboBox()
        fm.addItems(["Standard", "Super Silent", "Dust Cleaning", "Performance"])
        self.fan_combos.append(fm)
        fm.currentIndexChanged.connect(self.auto_apply_change)
        self.rows['fan_main'] = self._create_row("Active Cooling Policy", "Controls the EC fan curve behavior.", fm)
        layout.addWidget(self.rows['fan_main'])
        
        # TDP Customization
        tdp_row = QFrame()
        tdp_row.setObjectName("SettingsRow")
        self.rows['tdp'] = tdp_row
        tdp_layout = QGridLayout(tdp_row)
        tdp_layout.setContentsMargins(20, 15, 20, 15)
        
        tdp_title_v = QVBoxLayout()
        lbl_tdp_title = QLabel("Custom TDP (RyzenAdj)")
        lbl_tdp_title.setProperty("class", "RowTitle")
        tdp_title_v.addWidget(lbl_tdp_title)
        lbl_tdp_sub = QLabel("Override hardware power limits in mW.")
        lbl_tdp_sub.setProperty("class", "RowSubtitle")
        tdp_title_v.addWidget(lbl_tdp_sub)
        tdp_title_v.addStretch()
        tdp_layout.addLayout(tdp_title_v, 0, 0, 3, 1)
        
        tdp_layout.addWidget(QLabel("STAPM:"), 0, 1, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        spin_stapm = QSpinBox()
        spin_stapm.setRange(10000, 100000)
        spin_stapm.setSingleStep(1000)
        self.tdp_spins.append(spin_stapm)
        tdp_layout.addWidget(spin_stapm, 0, 2)
        
        tdp_layout.addWidget(QLabel("Fast:"), 1, 1, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        spin_fast = QSpinBox()
        spin_fast.setRange(10000, 100000)
        spin_fast.setSingleStep(1000)
        self.tdp_spins.append(spin_fast)
        tdp_layout.addWidget(spin_fast, 1, 2)
        
        tdp_layout.addWidget(QLabel("Slow:"), 2, 1, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        spin_slow = QSpinBox()
        spin_slow.setRange(10000, 100000)
        spin_slow.setSingleStep(1000)
        self.tdp_spins.append(spin_slow)
        tdp_layout.addWidget(spin_slow, 2, 2)
        
        btn_apply_tdp = QPushButton("Apply TDP")
        btn_apply_tdp.setObjectName("ApplyBtn")
        btn_apply_tdp.clicked.connect(self.apply_tdp)
        tdp_layout.addWidget(btn_apply_tdp, 3, 2)
        layout.addWidget(tdp_row)
        
        # Display Section
        lbl_disp = QLabel("Display Section")
        lbl_disp.setObjectName("SectionTitle")
        layout.addWidget(lbl_disp)
        
        dr = QComboBox()
        dr.addItems(["Native"])
        dr.setEnabled(False)
        dr_row = self._create_row("Resolution", "Managed by OS.", dr)
        dr_row.setEnabled(False)
        layout.addWidget(dr_row)
        
        ds = QComboBox()
        ds.addItems(["Native"])
        ds.setEnabled(False)
        ds_row = self._create_row("Scaling (DPI)", "Managed by OS.", ds)
        ds_row.setEnabled(False)
        layout.addWidget(ds_row)
        
        # System Controls
        lbl_sys = QLabel("System Controls")
        lbl_sys.setObjectName("SectionTitle")
        layout.addWidget(lbl_sys)
        
        kb = QComboBox()
        kb.addItems(["Off"])
        kb.setEnabled(False)
        kb_row = self._create_row("Keyboard Backlight", "OpenRGB missing or unsupported.", kb)
        kb_row.setEnabled(False)
        layout.addWidget(kb_row)
        
        tt = QComboBox()
        tt.addItems(["On"])
        tt.setEnabled(False)
        tt_row = self._create_row("Touchpad Toggle", "Managed by OS desktop environment.", tt)
        tt_row.setEnabled(False)
        layout.addWidget(tt_row)
        
        fn = QComboBox()
        fn.addItems(["Off", "On"])
        self.fn_combos.append(fn)
        fn.currentIndexChanged.connect(self.auto_apply_change)
        self.rows['fn'] = self._create_row("Fn Lock", "Toggle media keys vs F1-F12 primary functions.", fn)
        layout.addWidget(self.rows['fn'])
        
        wk = QComboBox()
        wk.addItems(["Off"])
        wk.setEnabled(False)
        wk_row = self._create_row("Windows Key Lock", "Unsupported.", wk)
        wk_row.setEnabled(False)
        layout.addWidget(wk_row)
        
        layout.addStretch()
        return page

    def create_battery_page(self):
        page, layout = self._create_scroll_page("Battery Details")
        
        grid = QGridLayout()
        grid.setVerticalSpacing(20)
        grid.setHorizontalSpacing(50)
        
        self.bat_labels = {}
        fields = [
            ("Battery %", "percent"),
            ("Charging state", "status"),
            ("Current capacity", "current"),
            ("Full capacity", "full"),
            ("Design capacity", "design"),
            ("Health %", "health"),
            ("Cycle count", "cycles")
        ]
        
        for i, (label, key) in enumerate(fields):
            r, c = divmod(i, 2)
            lbl_title = QLabel(label)
            lbl_title.setStyleSheet("font-size: 14px; color: #aaaaaa;")
            lbl_val = QLabel("N/A")
            lbl_val.setStyleSheet("font-size: 18px; font-weight: bold; color: #ffffff;")
            
            v = QVBoxLayout()
            v.addWidget(lbl_title)
            v.addWidget(lbl_val)
            self.bat_labels[key] = lbl_val
            grid.addLayout(v, r, c)
            
        frame = QFrame()
        frame.setObjectName("SettingsRow")
        # Give battery grid some internal padding so it acts like a card
        blayout = QVBoxLayout(frame)
        blayout.setContentsMargins(40, 40, 40, 40)
        blayout.addLayout(grid)
        
        layout.addWidget(frame)
        layout.addStretch()
        return page

    def create_actions_page(self):
        page, layout = self._create_scroll_page("Actions & Automation")
        
        lbl_info = QLabel("Event-driven automation engine for hardware profiles.")
        lbl_info.setStyleSheet("color: #aaaaaa; margin-bottom: 10px;")
        layout.addWidget(lbl_info)
        
        mt = QComboBox()
        mt.addItems(["Disabled"])
        mt.setEnabled(False)
        mt_row = self._create_row("Master Toggle", "Enable or disable automation rules globally.", mt, "Automation daemon not fully implemented.")
        mt_row.setEnabled(False)
        layout.addWidget(mt_row)
        
        lbl_trig = QLabel("Triggers & Actions")
        lbl_trig.setObjectName("SectionTitle")
        layout.addWidget(lbl_trig)
        
        tr = QComboBox()
        tr.addItems(["AC Connected", "AC Disconnected"])
        tr.setEnabled(False)
        tr_row = self._create_row("Available Triggers", "Select trigger conditions.", tr)
        tr_row.setEnabled(False)
        layout.addWidget(tr_row)
        
        ac = QComboBox()
        ac.addItems(["Set Power Mode", "Set GPU Mode"])
        ac.setEnabled(False)
        ac_row = self._create_row("Mapped Actions", "Define behavior upon trigger.", ac)
        ac_row.setEnabled(False)
        layout.addWidget(ac_row)
        
        layout.addStretch()
        return page

    def create_settings_page(self):
        page, layout = self._create_scroll_page("Settings")
        
        lbl_gen = QLabel("General")
        lbl_gen.setObjectName("SectionTitle")
        layout.addWidget(lbl_gen)
        
        lang = QComboBox()
        lang.addItems(["System Default", "English"])
        layout.addWidget(self._create_row("Language", "Set application language.", lang))
        
        theme = QComboBox()
        theme.addItems(["Dark", "Light", "System"])
        layout.addWidget(self._create_row("Theme", "Application appearance.", theme))
        
        lbl_beh = QLabel("Behavior")
        lbl_beh.setObjectName("SectionTitle")
        layout.addWidget(lbl_beh)
        
        autorun = QComboBox()
        autorun.addItems(["Off"])
        autorun.setEnabled(False)
        autorun_row = self._create_row("Autorun", "Start with system.", autorun)
        autorun_row.setEnabled(False)
        layout.addWidget(autorun_row)
        
        bl = QComboBox()
        bl.addItems(["Disabled"])
        bl.setEnabled(False)
        bl_row = self._create_row("Boot Logo", "Change UEFI boot logo.", bl, "Not implemented. Missing firmware map.")
        bl_row.setEnabled(False)
        layout.addWidget(bl_row)
        
        layout.addStretch()
        return page

    def create_about_page(self):
        page, layout = self._create_scroll_page("About")
        
        frame = QFrame()
        frame.setObjectName("SettingsRow")
        v = QVBoxLayout(frame)
        v.setContentsMargins(30, 30, 30, 30)
        v.setSpacing(10)
        
        title = QLabel("Lenovo Vantage Linux Unofficial")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        v.addWidget(title)
        
        v.addWidget(QLabel("A robust, native hardware control suite built for Lenovo laptops running on Linux."))
        v.addSpacing(15)
        v.addWidget(QLabel("<b>Version:</b> 1.0.0-initial-release"))
        v.addWidget(QLabel("<b>Backend:</b> D-Bus System Daemon"))
        v.addWidget(QLabel("<b>Dependencies:</b> supergfxctl, ryzenadj, power-profiles-daemon"))
        
        lbl_github = QLabel('<b>GitHub:</b> <a href="https://github.com/nightcodex7/lenovo-vantage-unofficial-linux" style="color: #0078d4; text-decoration: none;">nightcodex7/lenovo-vantage-unofficial-linux</a>')
        lbl_github.setOpenExternalLinks(True)
        v.addWidget(lbl_github)
        
        layout.addWidget(frame)
        layout.addStretch()
        return page

    # --- LOGIC ---
    
    def apply_cap(self, widget, cap_dict, partial_warning=""):
        if not isinstance(cap_dict, dict) or not widget:
            return
        supported = cap_dict.get("supported", False)
        partial = cap_dict.get("partial", False)
        reason = cap_dict.get("reason", "Not supported by hardware.")
        
        if not supported:
            widget.setEnabled(False)
            widget.setToolTip(reason)
        elif partial:
            widget.setEnabled(True)
            widget.setToolTip(reason + f"\n{partial_warning}")
        else:
            widget.setEnabled(True)
            widget.setToolTip("")

    def auto_apply_change(self):
        sender = self.sender()
        if not sender or not sender.isEnabled():
            return
            
        errors = []
        try:
            if sender in self.pm_combos:
                pm = "balanced" if sender.currentText() == "Balance" else sender.currentText().lower()
                self.svc.iface.SetPowerMode(pm)
            elif sender in self.bat_combos:
                self.svc.iface.SetConservation(sender.currentText() == "Conservation")
            elif sender in self.usb_combos:
                self.svc.iface.SetUsbCharging(sender.currentText() == "On")
            elif sender in self.ib_combos:
                self.svc.iface.SetInstantBoot(sender.currentText() == "On")
            elif sender in self.fs_combos:
                self.svc.iface.SetFlipToStart(sender.currentText() == "On")
            elif sender in self.gpu_combos:
                self.svc.iface.SetDgpuMode(sender.currentText().lower())
            elif sender in self.fan_combos:
                fm = sender.currentText().lower().replace(" ", "_")
                self.svc.iface.SetFanMode(fm)
            elif sender in self.fn_combos:
                self.svc.iface.SetFnLock(sender.currentText() == "On")
        except Exception as e:
            errors.append(str(e))
            
        if errors:
            QMessageBox.warning(self, "Change Failed", "\n".join(errors))
            
        self.load_state()

    def apply_tdp(self):
        try:
            self.svc.iface.SetRyzenTdp(self.tdp_spins[0].value(), self.tdp_spins[1].value(), self.tdp_spins[2].value())
        except Exception as e:
            QMessageBox.warning(self, "TDP Error", str(e))

    def load_state(self):
        try:
            raw_caps = self.svc.iface.GetAllCapabilities()
            caps = {}
            for k, v in raw_caps.items():
                try:
                    caps[str(k)] = {str(ik): (bool(iv) if ik in ['supported', 'partial'] else str(iv)) for ik, iv in v.items()}
                except: pass
                
            self.apply_cap(self.rows.get('power_dash'), caps.get("power", {}))
            self.apply_cap(self.rows.get('power_main'), caps.get("power", {}))
            
            self.apply_cap(self.rows.get('battery'), caps.get("battery", {}))
            
            sys_cap = caps.get("system", {})
            self.apply_cap(self.rows.get('fn'), sys_cap)
            self.apply_cap(self.rows.get('ib'), sys_cap)
            self.apply_cap(self.rows.get('fs'), sys_cap)
            self.apply_cap(self.rows.get('usb'), sys_cap)
            
            self.apply_cap(self.rows.get('gpu_dash'), caps.get("gpu", {}))
            self.apply_cap(self.rows.get('gpu_main'), caps.get("gpu", {}))
            
            self.apply_cap(self.rows.get('fan_dash'), caps.get("fan", {}))
            self.apply_cap(self.rows.get('fan_main'), caps.get("fan", {}))
            
            self.apply_cap(self.rows.get('tdp'), caps.get("ryzenadj", {}), "Missing ryzenadj binary.")
        except Exception: pass

        def _sync(combos, val):
            for c in combos:
                c.blockSignals(True)
                c.setCurrentText(val)
                c.blockSignals(False)

        try:
            pm = str(self.svc.iface.GetPowerMode()).lower()
            _sync(self.pm_combos, "Quiet" if "quiet" in pm else "Performance" if "performance" in pm else "Balance")
        except: pass
        
        try:
            _sync(self.bat_combos, "Conservation" if bool(self.svc.iface.GetConservation()) else "Normal")
        except: pass

        try:
            _sync(self.usb_combos, "On" if bool(self.svc.iface.GetUsbCharging()) else "Off")
        except: pass
        
        try:
            _sync(self.fn_combos, "On" if bool(self.svc.iface.GetFnLock()) else "Off")
        except: pass
        
        try:
            _sync(self.ib_combos, "On" if bool(self.svc.iface.GetInstantBoot()) else "Off")
        except: pass
        
        try:
            _sync(self.fs_combos, "On" if bool(self.svc.iface.GetFlipToStart()) else "Off")
        except: pass
        
        try:
            gpu_mode = str(self.svc.iface.GetDgpuMode()).lower()
            _sync(self.gpu_combos, "Integrated" if "integrated" in gpu_mode else "Dedicated" if "dedicated" in gpu_mode or "nvidia" in gpu_mode else "Hybrid")
        except: pass
        
        try:
            fm = str(self.svc.iface.GetFanMode()).lower()
            _sync(self.fan_combos, "Super Silent" if "super" in fm else "Dust Cleaning" if "dust" in fm else "Performance" if "performance" in fm else "Standard")
        except: pass
        
        try:
            tdp = self.svc.iface.GetRyzenTdp()
            if self.tdp_spins:
                for s in self.tdp_spins: s.blockSignals(True)
                self.tdp_spins[0].setValue(int(tdp.get("stapm", 45000)))
                self.tdp_spins[1].setValue(int(tdp.get("fast", 45000)))
                self.tdp_spins[2].setValue(int(tdp.get("slow", 45000)))
                for s in self.tdp_spins: s.blockSignals(False)
        except: pass

    def update_sensors(self):
        try:
            s = self.svc.iface.GetSensors()
            cpu = float(s.get('cpu_temp', 0))
            gpu = float(s.get('gpu_temp', 0))
            cpu_util = float(s.get('cpu_usage', 0))
            gpu_util = float(s.get('gpu_usage', 0))
            fan = int(s.get('fan_rpm', 0))
            
            self.pb_cpu.setValue(int(cpu_util))
            self.lbl_cpu_util.setText(f"{cpu_util:.1f}%")
            self.pb_cput.setValue(int(cpu))
            self.lbl_cpu_temp.setText(f"{cpu:.1f} °C")
            self.pb_cpuf.setValue(int(fan / 50 if fan > 0 else 0))
            self.lbl_cpu_fan.setText(f"{fan} RPM")
            
            self.pb_gpu.setValue(int(gpu_util))
            self.lbl_gpu_util.setText(f"{gpu_util:.1f}%")
            self.pb_gput.setValue(int(gpu))
            self.lbl_gpu_temp.setText(f"{gpu:.1f} °C")
        except Exception:
            pass
            
        if hasattr(self, 'bat_labels'):
            binfo = get_battery_info()
            for k, lbl in self.bat_labels.items():
                if k in binfo:
                    val = binfo[k]
                    if val != "N/A":
                        if k in ["current", "full", "design"]: val = str(int(val)//1000) + " mAh/mWh"
                        elif k == "percent": val += "%"
                    lbl.setText(val)

def main():
    # Enforce native Wayland/X11 scaling and session management across all DEs
    os.environ.setdefault("QT_QPA_PLATFORM", "wayland;xcb")
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("/usr/share/icons/hicolor/scalable/apps/vantage.png"))
    try:
        svc = VantageService()
    except Exception as e:
        QMessageBox.critical(None, "Daemon Error", str(e))
        sys.exit(1)
        
    gui = VantageGUI(svc)
    gui.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
