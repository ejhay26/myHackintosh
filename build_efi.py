import os
import shutil
import uuid
import plistlib
import subprocess

print("=== Starting OpenCore EFI Assembly for Lenovo Ideapad 300-14ISK (DEBUG Build) ===")

# Base paths
WORKSPACE = os.path.dirname(os.path.abspath(__file__))
EFI_DIR = os.path.join(WORKSPACE, "EFI")
BOOT_DIR = os.path.join(EFI_DIR, "BOOT")
OC_DIR = os.path.join(EFI_DIR, "OC")
ACPI_DIR = os.path.join(OC_DIR, "ACPI")
DRIVERS_DIR = os.path.join(OC_DIR, "Drivers")
KEXTS_DIR = os.path.join(OC_DIR, "Kexts")
RESOURCES_DIR = os.path.join(OC_DIR, "Resources")
TOOLS_DIR = os.path.join(OC_DIR, "Tools")

# Clean existing EFI folder if present
if os.path.exists(EFI_DIR):
    shutil.rmtree(EFI_DIR)

for d in [BOOT_DIR, OC_DIR, ACPI_DIR, DRIVERS_DIR, KEXTS_DIR, RESOURCES_DIR, TOOLS_DIR]:
    os.makedirs(d, exist_ok=True)

# 1. Copy Bootloader binaries from tools/OpenCore_DEBUG
shutil.copy2("tools/OpenCore_DEBUG/X64/EFI/BOOT/BOOTx64.efi", os.path.join(BOOT_DIR, "BOOTx64.efi"))
shutil.copy2("tools/OpenCore_DEBUG/X64/EFI/OC/OpenCore.efi", os.path.join(OC_DIR, "OpenCore.efi"))

# 2. Copy Drivers (DEBUG versions + official OpenHfsPlus.efi)
shutil.copy2("tools/OpenCore_DEBUG/X64/EFI/OC/Drivers/OpenRuntime.efi", os.path.join(DRIVERS_DIR, "OpenRuntime.efi"))
shutil.copy2("tools/OpenCore_DEBUG/X64/EFI/OC/Drivers/OpenHfsPlus.efi", os.path.join(DRIVERS_DIR, "OpenHfsPlus.efi"))
shutil.copy2("tools/OpenCore_DEBUG/X64/EFI/OC/Drivers/ResetNvramEntry.efi", os.path.join(DRIVERS_DIR, "ResetNvramEntry.efi"))

# 3. Copy Tools
shutil.copy2("tools/OpenCore_DEBUG/X64/EFI/OC/Tools/OpenShell.efi", os.path.join(TOOLS_DIR, "OpenShell.efi"))

# 4. Copy Resources (Canopy GUI icons, fonts, audio)
shutil.copytree("tools/OcBinaryData/Resources", RESOURCES_DIR, dirs_exist_ok=True)

# 5. Copy ACPI Tables
acpi_sources = [
    ("tools/Getting-Started-With-ACPI/extra-files/compiled/SSDT-PLUG-DRTNIA.aml", "SSDT-PLUG-DRTNIA.aml"),
    ("tools/Getting-Started-With-ACPI/extra-files/compiled/SSDT-EC-USBX-LAPTOP.aml", "SSDT-EC-USBX-LAPTOP.aml"),
    ("SSDT-PNLF-NEW.aml", "SSDT-PNLF.aml"),
]

for src, dst_name in acpi_sources:
    shutil.copy2(src, os.path.join(ACPI_DIR, dst_name))
    print(f"Copied ACPI table: {dst_name}")

# 6. Copy Kexts
kexts_to_copy = [
    ("tools/kexts_extracted/Lilu/Lilu.kext", "Lilu.kext"),
    ("tools/kexts_extracted/VirtualSMC/Kexts/VirtualSMC.kext", "VirtualSMC.kext"),
    ("tools/kexts_extracted/VirtualSMC/Kexts/SMCBatteryManager.kext", "SMCBatteryManager.kext"),
    ("tools/kexts_extracted/VirtualSMC/Kexts/SMCProcessor.kext", "SMCProcessor.kext"),
    ("tools/kexts_extracted/WhateverGreen/WhateverGreen.kext", "WhateverGreen.kext"),
    ("tools/kexts_extracted/AppleALC/AppleALC.kext", "AppleALC.kext"),
    ("tools/kexts_extracted/ECEnabler/ECEnabler.kext", "ECEnabler.kext"),
    ("tools/kexts_extracted/RealtekRTL8111/RealtekRTL8111-V3.0.0/Release/RealtekRTL8111.kext", "RealtekRTL8111.kext"),
    ("tools/kexts_extracted/BrightnessKeys/BrightnessKeys.kext", "BrightnessKeys.kext"),
    ("tools/kexts_extracted/VoodooPS2/VoodooPS2Controller.kext", "VoodooPS2Controller.kext"),
    ("tools/kexts_extracted/USBToolBox/USBToolBox.kext", "USBToolBox.kext"),
    ("UTBMap.kext", "UTBMap.kext"),
]

for src, dst_name in kexts_to_copy:
    dst_path = os.path.join(KEXTS_DIR, dst_name)
    shutil.copytree(src, dst_path, dirs_exist_ok=True)
    print(f"Copied Kext: {dst_name}")

# 7. Generate clean config.plist from Sample.plist
sample_plist_path = "tools/OpenCore_DEBUG/Docs/Sample.plist"
if not os.path.exists(sample_plist_path):
    sample_plist_path = "tools/OpenCore/Docs/Sample.plist"

with open(sample_plist_path, "rb") as f:
    config = plistlib.load(f)

# Configure ACPI
config["ACPI"]["Add"] = [
    {
        "Comment": "Native CPU Power Management (Plugin Type 1) for Core i5-6200U",
        "Enabled": True,
        "Path": "SSDT-PLUG-DRTNIA.aml"
    },
    {
        "Comment": "Fake Embedded Controller and USBX Power properties for Laptop",
        "Enabled": True,
        "Path": "SSDT-EC-USBX-LAPTOP.aml"
    },
    {
        "Comment": "Native Backlight Control for Skylake HD 520 (_UID 16)",
        "Enabled": True,
        "Path": "SSDT-PNLF.aml"
    }
]

config["ACPI"]["Delete"] = []
config["ACPI"]["Patch"] = []
config["ACPI"]["Quirks"]["ResetLogoStatus"] = False

# Configure Booter
booter_quirks = config["Booter"]["Quirks"]
booter_quirks["AvoidRuntimeDefrag"] = True
booter_quirks["DevirtualiseMmio"] = False
booter_quirks["DisableSingleUser"] = False
booter_quirks["DisableVariableWrite"] = False
booter_quirks["DiscardHibernateMap"] = False
booter_quirks["EnableSafeModeSlide"] = True
booter_quirks["EnableWriteUnprotector"] = True
booter_quirks["ForceBooterSignature"] = False
booter_quirks["ForceExitBootServices"] = False
booter_quirks["ProtectMemoryRegions"] = False
booter_quirks["ProtectSecureBoot"] = False
booter_quirks["ProtectUefiServices"] = False
booter_quirks["ProvideCustomSlide"] = True
booter_quirks["ProvideMaxSlide"] = 0
booter_quirks["RebuildAppleMemoryMap"] = False
booter_quirks["ResizeAppleGpuBars"] = -1
booter_quirks["SetupVirtualMap"] = True
booter_quirks["SignalAppleOS"] = False
booter_quirks["SyncRuntimePermissions"] = False

# Extracted EDID for the replacement 1600x900 screen (CMN14A3)
edid_1600x900 = bytes.fromhex(
    "00ffffffffffff000daea314000000001f160104951f117802b535945553932923505400000001010101010101010101010101010101"
    "1c2a405461841a303020350035ae1000001a131c405461841a303020350035ae1000001a000000000000000000000000000000000000"
    "00000002000c3dff0c3c7d1511237d000000006e"
)

# Configure DeviceProperties
config["DeviceProperties"]["Add"] = {
    "PciRoot(0x0)/Pci(0x2,0x0)": {
        "AAPL,ig-platform-id": bytes.fromhex("00001659"),
        "device-id": bytes.fromhex("16590000"),
        "framebuffer-patch-enable": bytes.fromhex("01000000"),
        "framebuffer-stolenmem": bytes.fromhex("00003001"),
        "framebuffer-fbmem": bytes.fromhex("00009000"),
        "enable-maxmem": bytes.fromhex("01000000"),
        "enable-dvmt-calc-fix": bytes.fromhex("01000000"),
        "framebuffer-con1-enable": bytes.fromhex("01000000"),
        "framebuffer-con1-type": bytes.fromhex("00080000")
    }
}
config["DeviceProperties"]["Delete"] = {}

# Configure Kernel
config["Kernel"]["Add"] = [
    {
        "Arch": "x86_64",
        "BundlePath": "Lilu.kext",
        "Comment": "Patch Engine",
        "Enabled": True,
        "ExecutablePath": "Contents/MacOS/Lilu",
        "MaxKernel": "",
        "MinKernel": "",
        "PlistPath": "Contents/Info.plist"
    },
    {
        "Arch": "x86_64",
        "BundlePath": "VirtualSMC.kext",
        "Comment": "SMC Emulator",
        "Enabled": True,
        "ExecutablePath": "Contents/MacOS/VirtualSMC",
        "MaxKernel": "",
        "MinKernel": "",
        "PlistPath": "Contents/Info.plist"
    },
    {
        "Arch": "x86_64",
        "BundlePath": "SMCBatteryManager.kext",
        "Comment": "Battery Readout",
        "Enabled": True,
        "ExecutablePath": "Contents/MacOS/SMCBatteryManager",
        "MaxKernel": "",
        "MinKernel": "",
        "PlistPath": "Contents/Info.plist"
    },
    {
        "Arch": "x86_64",
        "BundlePath": "SMCProcessor.kext",
        "Comment": "CPU Temp Sensor",
        "Enabled": True,
        "ExecutablePath": "Contents/MacOS/SMCProcessor",
        "MaxKernel": "",
        "MinKernel": "",
        "PlistPath": "Contents/Info.plist"
    },
    {
        "Arch": "x86_64",
        "BundlePath": "WhateverGreen.kext",
        "Comment": "Graphics Driver",
        "Enabled": True,
        "ExecutablePath": "Contents/MacOS/WhateverGreen",
        "MaxKernel": "",
        "MinKernel": "",
        "PlistPath": "Contents/Info.plist"
    },
    {
        "Arch": "x86_64",
        "BundlePath": "AppleALC.kext",
        "Comment": "Audio Driver",
        "Enabled": True,
        "ExecutablePath": "Contents/MacOS/AppleALC",
        "MaxKernel": "",
        "MinKernel": "",
        "PlistPath": "Contents/Info.plist"
    },
    {
        "Arch": "x86_64",
        "BundlePath": "ECEnabler.kext",
        "Comment": "Enables 16-bit EC fields for Lenovo Battery",
        "Enabled": True,
        "ExecutablePath": "Contents/MacOS/ECEnabler",
        "MaxKernel": "",
        "MinKernel": "",
        "PlistPath": "Contents/Info.plist"
    },
    {
        "Arch": "x86_64",
        "BundlePath": "RealtekRTL8111.kext",
        "Comment": "Gigabit Ethernet",
        "Enabled": True,
        "ExecutablePath": "Contents/MacOS/RealtekRTL8111",
        "MaxKernel": "",
        "MinKernel": "",
        "PlistPath": "Contents/Info.plist"
    },
    {
        "Arch": "x86_64",
        "BundlePath": "BrightnessKeys.kext",
        "Comment": "Fn Brightness Keys",
        "Enabled": True,
        "ExecutablePath": "Contents/MacOS/BrightnessKeys",
        "MaxKernel": "",
        "MinKernel": "",
        "PlistPath": "Contents/Info.plist"
    },
    {
        "Arch": "x86_64",
        "BundlePath": "USBToolBox.kext",
        "Comment": "USB Driver Engine",
        "Enabled": True,
        "ExecutablePath": "Contents/MacOS/USBToolBox",
        "MaxKernel": "",
        "MinKernel": "",
        "PlistPath": "Contents/Info.plist"
    },
    {
        "Arch": "x86_64",
        "BundlePath": "UTBMap.kext",
        "Comment": "Custom USB Port Map for Lenovo Ideapad 300",
        "Enabled": True,
        "ExecutablePath": "",
        "MaxKernel": "",
        "MinKernel": "",
        "PlistPath": "Contents/Info.plist"
    },
    {
        "Arch": "x86_64",
        "BundlePath": "VoodooPS2Controller.kext",
        "Comment": "PS/2 Controller",
        "Enabled": True,
        "ExecutablePath": "Contents/MacOS/VoodooPS2Controller",
        "MaxKernel": "",
        "MinKernel": "",
        "PlistPath": "Contents/Info.plist"
    },
    {
        "Arch": "x86_64",
        "BundlePath": "VoodooPS2Controller.kext/Contents/PlugIns/VoodooInput.kext",
        "Comment": "Generic Input Engine",
        "Enabled": True,
        "ExecutablePath": "Contents/MacOS/VoodooInput",
        "MaxKernel": "",
        "MinKernel": "",
        "PlistPath": "Contents/Info.plist"
    },
    {
        "Arch": "x86_64",
        "BundlePath": "VoodooPS2Controller.kext/Contents/PlugIns/VoodooPS2Keyboard.kext",
        "Comment": "PS/2 Keyboard",
        "Enabled": True,
        "ExecutablePath": "Contents/MacOS/VoodooPS2Keyboard",
        "MaxKernel": "",
        "MinKernel": "",
        "PlistPath": "Contents/Info.plist"
    },
    {
        "Arch": "x86_64",
        "BundlePath": "VoodooPS2Controller.kext/Contents/PlugIns/VoodooPS2Trackpad.kext",
        "Comment": "Synaptics PS/2 Trackpad",
        "Enabled": True,
        "ExecutablePath": "Contents/MacOS/VoodooPS2Trackpad",
        "MaxKernel": "",
        "MinKernel": "",
        "PlistPath": "Contents/Info.plist"
    },
    {
        "Arch": "x86_64",
        "BundlePath": "VoodooPS2Controller.kext/Contents/PlugIns/VoodooPS2Mouse.kext",
        "Comment": "PS/2 Mouse (Disabled in favor of Trackpad)",
        "Enabled": False,
        "ExecutablePath": "Contents/MacOS/VoodooPS2Mouse",
        "MaxKernel": "",
        "MinKernel": "",
        "PlistPath": "Contents/Info.plist"
    }
]

config["Kernel"]["Block"] = []
config["Kernel"]["Force"] = []
config["Kernel"]["Patch"] = []

kernel_quirks = config["Kernel"]["Quirks"]
kernel_quirks["AppleCpuPmCfgLock"] = False
kernel_quirks["AppleXcpmCfgLock"] = True
kernel_quirks["AppleXcpmExtraMsrs"] = False
kernel_quirks["AppleXcpmForceBoost"] = False
kernel_quirks["CustomPciSerialDevice"] = False
kernel_quirks["CustomSMBIOSGuid"] = True
kernel_quirks["DisableIoMapper"] = True
kernel_quirks["DisableIoMapperMapping"] = False
kernel_quirks["DisableLinkeditJettison"] = True
kernel_quirks["DisableRtcChecksum"] = False
kernel_quirks["ExtendBTFeatureFlags"] = False
kernel_quirks["ExternalDiskIcons"] = False
kernel_quirks["ForceAquantiaEthernet"] = False
kernel_quirks["ForceSecureBootScheme"] = False
kernel_quirks["IncreasePciBarSize"] = False
kernel_quirks["LapicKernelPanic"] = False
kernel_quirks["LegacyCommpage"] = False
kernel_quirks["PanicNoKextDump"] = True
kernel_quirks["PowerTimeoutKernelPanic"] = True
kernel_quirks["ProvideCurrentCpuInfo"] = False
kernel_quirks["SetApfsTrimTimeout"] = 0
kernel_quirks["ThirdPartyDrives"] = False
kernel_quirks["XhciPortLimit"] = False

# Configure Misc
config["Misc"]["Boot"]["ConsoleAttributes"] = 0
config["Misc"]["Boot"]["HibernateMode"] = "None"
config["Misc"]["Boot"]["HibernateSkipsPicker"] = False
config["Misc"]["Boot"]["HideAuxiliary"] = True
config["Misc"]["Boot"]["LauncherOption"] = "Disabled"
config["Misc"]["Boot"]["LauncherPath"] = "Default"
config["Misc"]["Boot"]["PickerAttributes"] = 17
config["Misc"]["Boot"]["PickerAudioAssist"] = False
config["Misc"]["Boot"]["PickerMode"] = "Builtin"  # Text picker prevents black screen on laptop panel
config["Misc"]["Boot"]["PickerVariant"] = "Auto"
config["Misc"]["Boot"]["PollAppleHotKeys"] = True
config["Misc"]["Boot"]["ShowPicker"] = True
config["Misc"]["Boot"]["TakeoffDelay"] = 0
config["Misc"]["Boot"]["Timeout"] = 0  # 0 = No auto-boot timeout; wait for user selection

config["Misc"]["Debug"]["AppleDebug"] = True
config["Misc"]["Debug"]["ApplePanic"] = True
config["Misc"]["Debug"]["DisableWatchDog"] = True
config["Misc"]["Debug"]["DisplayDelay"] = 0
config["Misc"]["Debug"]["DisplayLevel"] = 2147483650
config["Misc"]["Debug"]["LogModules"] = "*"
config["Misc"]["Debug"]["SysReport"] = False
config["Misc"]["Debug"]["Target"] = 67  # Screen + File logging

config["Misc"]["Security"]["AllowSetDefault"] = True
config["Misc"]["Security"]["ApECID"] = 0
config["Misc"]["Security"]["AuthRestart"] = False
config["Misc"]["Security"]["BlacklistAppleUpdate"] = True
config["Misc"]["Security"]["DmgLoading"] = "Signed"
config["Misc"]["Security"]["EnablePassword"] = False
config["Misc"]["Security"]["ExposeSensitiveData"] = 15  # Full debug exposure
config["Misc"]["Security"]["HaltLevel"] = 2147483648
config["Misc"]["Security"]["PasswordHash"] = b""
config["Misc"]["Security"]["PasswordSalt"] = b""
config["Misc"]["Security"]["ScanPolicy"] = 0  # Scan all drives
config["Misc"]["Security"]["SecureBootModel"] = "Disabled"  # Disabled for Monterey install
config["Misc"]["Security"]["Vault"] = "Optional"

config["Misc"]["Tools"] = [
    {
        "Arguments": "",
        "Auxiliary": True,
        "Comment": "UEFI Shell",
        "Enabled": False,
        "Flavour": "OpenShell:UEFIShell:Shell",
        "FullNvramAccess": False,
        "Name": "OpenShell.efi",
        "Path": "OpenShell.efi",
        "RealPath": False,
        "TextMode": False
    }
]

# Configure NVRAM
config["NVRAM"]["Add"]["7C436110-AB2A-4BBB-A880-FE41995C9F82"] = {
    "ForceDisplayAlignment": False,
    "boot-args": "keepsyms=1 debug=0x100 -v alcid=3 -igfxdvmt amfi=0x80 amfi_get_out_of_my_way=1 ipc_control_port_options=0",
    "csr-active-config": bytes.fromhex("03080000"),
    "prev-lang:kbd": "en-US:0",
    "run-efi-updater": "No"
}
config["NVRAM"]["Add"]["4D1EDE05-38C7-4A6A-9CC6-4BCCA8B38C14"] = {
    "DefaultBackgroundColor": bytes.fromhex("00000000")
}
config["NVRAM"]["Delete"] = {
    "4D1EDE05-38C7-4A6A-9CC6-4BCCA8B38C14": ["DefaultBackgroundColor"],
    "7C436110-AB2A-4BBB-A880-FE41995C9F82": ["boot-args", "csr-active-config"]
}
config["NVRAM"]["WriteFlash"] = True

# Configure PlatformInfo
config["PlatformInfo"]["Generic"] = {
    "AdviseFeatures": False,
    "MaxBIOSVersion": False,
    "MLB": "C027082004NHWVP1H",
    "ProcessorType": 0,
    "ROM": bytes.fromhex("112233445566"),
    "SpoofVendor": True,
    "SystemMemoryStatus": "Auto",
    "SystemProductName": "MacBookPro14,1",
    "SystemSerialNumber": "C02T9DYYHV29",
    "SystemUUID": "D40F55CB-7CD7-4712-A3CB-36C7FFF69DA6"
}
config["PlatformInfo"]["UpdateDataHub"] = True
config["PlatformInfo"]["UpdateNVRAM"] = True
config["PlatformInfo"]["UpdateSMBIOS"] = True
config["PlatformInfo"]["UpdateSMBIOSMode"] = "Custom"
config["PlatformInfo"]["UseRawUuidEncoding"] = False

# Configure UEFI
config["UEFI"]["APFS"]["EnableJumpstart"] = True
config["UEFI"]["APFS"]["GlobalConnect"] = False
config["UEFI"]["APFS"]["HideVerbose"] = True
config["UEFI"]["APFS"]["JumpstartHotPlug"] = False
config["UEFI"]["APFS"]["MinDate"] = -1
config["UEFI"]["APFS"]["MinVersion"] = -1

config["UEFI"]["Drivers"] = [
    {
        "Arguments": "",
        "Comment": "OpenCore Runtime",
        "Enabled": True,
        "LoadEarly": False,
        "Path": "OpenRuntime.efi"
    },
    {
        "Arguments": "",
        "Comment": "HFS+ File System Driver",
        "Enabled": True,
        "LoadEarly": False,
        "Path": "OpenHfsPlus.efi"
    },
    {
        "Arguments": "",
        "Comment": "Reset NVRAM Boot Option",
        "Enabled": True,
        "LoadEarly": False,
        "Path": "ResetNvramEntry.efi"
    }
]

config["UEFI"]["Input"]["KeyFiltering"] = False
config["UEFI"]["Input"]["KeyForgetThreshold"] = 5
config["UEFI"]["Input"]["KeySupport"] = True
config["UEFI"]["Input"]["KeySupportMode"] = "Auto"
config["UEFI"]["Input"]["KeySwap"] = False
config["UEFI"]["Input"]["PointerSupport"] = False
config["UEFI"]["Input"]["PointerSupportMode"] = ""
config["UEFI"]["Input"]["TimerResolution"] = 50000

config["UEFI"]["Output"]["ClearScreenOnModeSwitch"] = False
config["UEFI"]["Output"]["ConsoleFont"] = ""
config["UEFI"]["Output"]["ConsoleMode"] = ""
config["UEFI"]["Output"]["DirectGopRendering"] = False
config["UEFI"]["Output"]["ForceResolution"] = False
config["UEFI"]["Output"]["GopBurstMode"] = False
config["UEFI"]["Output"]["GopPassThrough"] = "Disabled"
config["UEFI"]["Output"]["IgnoreTextInGraphics"] = False
config["UEFI"]["Output"]["InitialMode"] = "Auto"
config["UEFI"]["Output"]["ProvideConsoleGop"] = True
config["UEFI"]["Output"]["ReconnectGraphicsOnConnect"] = False
config["UEFI"]["Output"]["ReconnectOnResChange"] = False
config["UEFI"]["Output"]["ReplaceTabWithSpace"] = False
config["UEFI"]["Output"]["Resolution"] = ""  # Empty string = use native 1366x768 firmware resolution
config["UEFI"]["Output"]["SanitiseClearScreen"] = False
config["UEFI"]["Output"]["TextRenderer"] = "BuiltinGraphics"
config["UEFI"]["Output"]["UgaPassThrough"] = False
config["UEFI"]["Output"]["UIScale"] = 0

config["UEFI"]["Quirks"]["ActivateHpetSupport"] = False
config["UEFI"]["Quirks"]["DisableSecurityPolicy"] = False
config["UEFI"]["Quirks"]["EnableVectorAcceleration"] = True
config["UEFI"]["Quirks"]["EnableVmx"] = False
config["UEFI"]["Quirks"]["ExitBootServicesDelay"] = 0
config["UEFI"]["Quirks"]["ForceOcWriteFlash"] = False
config["UEFI"]["Quirks"]["ForgeUefiSupport"] = False
config["UEFI"]["Quirks"]["IgnoreInvalidFlexRatio"] = False
config["UEFI"]["Quirks"]["ReleaseUsbOwnership"] = False  # False avoids resetting USB controller during boot
config["UEFI"]["Quirks"]["ReloadOptionRoms"] = False
config["UEFI"]["Quirks"]["RequestBootVarRouting"] = True
config["UEFI"]["Quirks"]["ResizeGpuBars"] = -1
config["UEFI"]["Quirks"]["ResizeUsePciRbIo"] = False
config["UEFI"]["Quirks"]["ShimRetainProtocol"] = False
config["UEFI"]["Quirks"]["TscSyncTimeout"] = 0
config["UEFI"]["Quirks"]["UnblockFsConnect"] = True  # True connects filesystem drivers on external USB

# Save final config.plist
config_out_path = os.path.join(OC_DIR, "config.plist")
with open(config_out_path, "wb") as f:
    plistlib.dump(config, f)
print(f"Pristine config.plist written to: {config_out_path}")

print("=== Validating configuration with ocvalidate ===")
ocvalidate_path = os.path.join(WORKSPACE, "tools/OpenCore_DEBUG/Utilities/ocvalidate/ocvalidate.exe")
result = subprocess.run([ocvalidate_path, config_out_path], capture_output=True, text=True)
print("Return Code:", result.returncode)
print("STDOUT:\n", result.stdout)
if result.stderr:
    print("STDERR:\n", result.stderr)

if result.returncode != 0:
    raise RuntimeError("ocvalidate failed!")

# Create archive of EFI
archive_path = os.path.join(WORKSPACE, "EFI-Lenovo-Ideapad-300-14ISK-Monterey-DEBUG")
shutil.make_archive(archive_path, 'zip', root_dir=WORKSPACE, base_dir="EFI")
print(f"Archived EFI to: {archive_path}.zip")

# Auto deploy to USB drive if S:\ exists
if os.path.exists("S:\\"):
    print("\n=== Auto-Deploying updated EFI to USB Drive (S:\\) ===")
    target_s_efi = "S:\\EFI"
    if os.path.exists(target_s_efi):
        shutil.rmtree(target_s_efi)
    shutil.copytree(EFI_DIR, target_s_efi)
    print("Successfully copied fresh EFI folder to S:\\EFI!")
    
    # Also clean out the old empty log file on S:\
    old_log = "S:\\opencore-2026-09-06-011226.txt"
    if os.path.exists(old_log):
        os.remove(old_log)
        print("Cleaned up previous empty log file from USB drive.")

print("\n=== OpenCore EFI DEBUG Build Completed Successfully! ===")
