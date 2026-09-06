import plistlib
import subprocess
import sys
import os

def toggle():
    subprocess.run(["mountvol", "B:", "/s"], check=True)
    try:
        config_path = r"B:\EFI\OC\config.plist"
        with open(config_path, "rb") as f:
            cfg = plistlib.load(f)
        
        current_mode = cfg["Misc"]["Boot"].get("PickerMode", "Builtin")
        if current_mode == "External":
            new_mode = "Builtin"
            print(">>> Switched PickerMode: [GRAPHICAL] -> [TEXT / BUILTIN]")
        else:
            new_mode = "External"
            print(">>> Switched PickerMode: [TEXT / BUILTIN] -> [GRAPHICAL / OPENCANOPY]")
            
        cfg["Misc"]["Boot"]["PickerMode"] = new_mode
        with open(config_path, "wb") as f:
            plistlib.dump(cfg, f)
            
        print(f"Successfully updated SSD EFI config.plist to '{new_mode}' mode.")
    finally:
        subprocess.run(["mountvol", "B:", "/d"])

if __name__ == "__main__":
    toggle()
