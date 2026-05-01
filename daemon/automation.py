import threading
import time
import json
import os
from pathlib import Path

CONFIG_DIR = "/etc/lenovo-vantage"
CONFIG_FILE = os.path.join(CONFIG_DIR, "automation.json")

class AutomationEngine:
    def __init__(self, service):
        self.service = service
        self.running = False
        self.thread = None
        self.last_ac_state = self.get_ac_state()
        self.rules = self.load_rules()

    def load_rules(self):
        try:
            if Path(CONFIG_FILE).exists():
                return json.loads(Path(CONFIG_FILE).read_text())
        except Exception as e:
            print(f"Failed to load automation rules: {e}")
        return {
            "on_ac_connect": {},
            "on_ac_disconnect": {}
        }

    def save_rules(self, rules):
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            Path(CONFIG_FILE).write_text(json.dumps(rules, indent=4))
            self.rules = rules
        except Exception as e:
            print(f"Failed to save automation rules: {e}")

    def get_ac_state(self):
        try:
            for supply in Path("/sys/class/power_supply").iterdir():
                if supply.name.startswith("AC") or supply.name.startswith("AD"):
                    try:
                        return (supply / "online").read_text().strip() == "1"
                    except Exception:
                        pass
        except Exception:
            pass
        return True # Default assume AC if unknown

    def apply_rule(self, rule_name):
        rule = self.rules.get(rule_name, {})
        print(f"Applying automation rule: {rule_name} -> {rule}")
        if "power_mode" in rule:
            try: 
                from features.power import set_power_mode
                set_power_mode(rule["power_mode"])
            except Exception as e: print(f"Auto-Power error: {e}")
        if "fan_mode" in rule:
            try: 
                from features.fan import set_fan_mode
                set_fan_mode(rule["fan_mode"])
            except Exception as e: print(f"Auto-Fan error: {e}")
        if "gpu_mode" in rule:
            try: 
                from features.gpu import set_dgpu_mode
                set_dgpu_mode(rule["gpu_mode"])
            except Exception as e: print(f"Auto-GPU error: {e}")

    def _monitor_loop(self):
        while self.running:
            current_ac = self.get_ac_state()
            if current_ac != self.last_ac_state:
                if current_ac:
                    self.apply_rule("on_ac_connect")
                else:
                    self.apply_rule("on_ac_disconnect")
                self.last_ac_state = current_ac
            time.sleep(2)

    def start(self):
        if not Path(CONFIG_FILE).exists():
            self.save_rules(self.rules)
            
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
