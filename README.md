# Lenovo Ideapad 300-14ISK Hackintosh (macOS Monterey 12.7.6)

[![OpenCore](https://img.shields.io/badge/OpenCore-1.0.7-blue.svg)](https://github.com/acidanthera/OpenCorePkg)
[![macOS](https://img.shields.io/badge/macOS-Monterey%2012.7.6-brightgreen.svg)](https://www.apple.com/macos/monterey/)
[![Architecture](https://img.shields.io/badge/Architecture-Intel%20Skylake-orange.svg)](https://ark.intel.com/content/www/us/en/ark/products/88193/intel-core-i5-6200u-processor-3m-cache-up-to-2-80-ghz.html)

A bare-metal, rock-solid OpenCore EFI configuration specifically tailored for the **Lenovo Ideapad 300-14ISK (Type 80Q6)** running **macOS Monterey 12.7.6**.

> [!IMPORTANT]
> **Maximum Supported OS: macOS Monterey 12.7.6**
> Due to hardware constraints—specifically the **locked 32 MB InsydeH2O BIOS DVMT Pre-Allocated limit** and the **upgraded 14.0" 1600×900 eDP display panel**—macOS Ventura (13.x) and newer cannot achieve hardware QE/CI graphics acceleration without modifying hidden BIOS NVRAM variables via `RU.efi` (which carries high risk of motherboards bricking).
> 
> On **macOS Monterey 12.7.6**, Intel Skylake HD 520 graphics are **100% natively supported by Apple in the kernel**. With the stability optimizations in this EFI, Monterey runs with full 60 FPS Metal hardware acceleration, zero stutters, zero 5-second freezes, and zero OCLP root patching.

---

## Hardware Specifications

| Component | Hardware Specification | Hackintosh Status |
| :--- | :--- | :--- |
| **Model** | Lenovo Ideapad 300-14ISK (Type 80Q6) | Supported |
| **CPU** | Intel Core i5-6200U (2 cores, 4 threads, 2.3 GHz - 2.8 GHz) | Native via `SSDT-PLUG-DRTNIA` (`plugin-type=1`) |
| **iGPU** | Intel HD Graphics 520 (Skylake GT2, Device ID `0x1916`) | Native QE/CI Metal acceleration, default ~1536 MB VRAM (intended default for stability; not 2048 MB) |
| **BIOS DVMT** | InsydeH2O UEFI BIOS (Locked to 32 MB DVMT) | Supported via `enable-dvmt-calc-fix` + 12MB/20MB rebalance |
| **dGPU** | AMD Radeon R5 M330 (`PEG0.PEGP`) | Disabled via `-wegnoegpu` & ACPI to conserve battery |
| **RAM** | 16 GB DDR3L-1600 MHz (Dual-Channel) | Supported |
| **Storage** | Kingston SA400S37240G 240GB SATA SSD | Multi-boot (Windows 10, macOS Monterey, Linux) |
| **Display (Custom)** | **14.0" 1600x900 HD+ (`CMN14A3` / N140FGE-EA2)** *(Upgraded from stock 1366x768)* | Native macOS Control Center brightness slider & dual-link timing |
| **Audio** | Realtek ALC236 / Conexant CX20751/2 | Working via `AppleALC.kext` (`alcid=3`) |
| **Ethernet** | Realtek RTL8168/8111 PCI Gigabit Ethernet | Working via `RealtekRTL8111.kext` v2.4.2 |
| **Touchpad** | Synaptics PS/2 Touchpad | Gestures working via `VoodooPS2Controller.kext` |
| **Keyboard** | Standard PS/2 Laptop Keyboard | Working via `VoodooPS2Keyboard.kext` *(Note: Keyboard brightness hotkeys are not functional; adjust brightness directly in macOS Control Center)* |
| **Battery** | Lenovo Dual-Cell / Embedded Controller | Working via `ECEnabler.kext` + `SMCBatteryManager.kext` |

---

## Stability Optimizations: Eliminating Stutters & 5-Second Freezes

Standard online Skylake EFIs frequently suffer from micro-freezes, game hangs, and 5-second stutters under heavy load or idle. This EFI resolves all three root causes:

### 1. 1600×900 Framebuffer Rebalance (`fbmem = 12 MB` / `stolenmem = 20 MB`)
* **The Problem:** Generic guides allocate `framebuffer-fbmem = 9 MB`, which is designed for stock **1366×768** panels ($1366 \times 768 \times 4 \times 2 = 8.39\text{ MB} < 9\text{ MB}$). On this upgraded **1600×900** panel:
  $$1600 \times 900 \times 4\text{ bytes} \times 2\text{ (double buffer)} = 11.52\text{ MB} > 9\text{ MB}$$
  Every ~5 seconds, periodic background window compositing overflowed the 9 MB boundary into unallocated memory, triggering an Intel GPU driver reset and temporary system freeze.
* **The Fix:**
  - `framebuffer-fbmem = <00 00 C0 00>` (12 MB)
  - `framebuffer-stolenmem = <00 00 40 01>` (20 MB)
  - Total: $12 + 20 = 32\text{ MB}$ (matching the 32 MB BIOS DVMT limit while giving the 1600×900 panel the full 11.52+ MB it requires).

### 2. Elimination of `rps-control` (RC6 Power-State Deadlock Fix)
* **The Problem:** Setting `rps-control = <01 00 00 00>` corrupts GPU frequency governor transitions during low-power RC6 idle states on Skylake Gen9 iGPUs, freezing 3D rendering while the mouse cursor still moves.
* **The Fix:** `rps-control` is **strictly omitted**, restoring smooth, native hardware power scaling.

### 3. QuickSync & Video Streaming Fix (`unfairgva = 1`)
* **The Problem:** Online boot-args often include `unfairgva=4`, which spoofs an `iMacPro1,1` board ID. Because `iMacPro1,1` lacks an integrated Intel GPU, macOS disabled Intel QuickSync hardware encoding, causing Discord, FaceTime, and WebRTC video to freeze or turn neon green.
* **The Fix:** Set `unfairgva=1` in `boot-args` to enable FairPlay DRM without disabling the Intel QuickSync hardware video engine.

---

## Display Configuration: 1600×900 (`CMN14A3`)

* **Direct EDID Injection (`AAPL00,override-no-connect`)**: Exact 128-byte hardware EDID for `CMN14A3` injected into `DeviceProperties` for timing synchronization.
* **Dual-Link Bus Bandwidth (`AAPL00,DualLink = <01 00 00 00>` & `@0,display-dual-link = <01 00 00 00>`)**: Enables dual-link pixel clock bandwidth required for horizontal resolutions $\ge 1600\text{px}$.
* **DisplayPort / eDP Connector (`framebuffer-con0-type = <00 04 00 00>`)**: Directs the DDI transmitter to drive internal eDP natively.
* **Skylake Backlight Modulation (`SSDT-PNLF.aml`)**: Injects `PNLF` properly nested inside `_SB.PCI0.GFX0` with `_UID = 0x10` (PWM frequency `0x56C`). Backlight intensity is adjusted directly through the macOS Control Center / System Settings slider *(keyboard brightness hotkeys are not mapped to ACPI on this model)*.

---

## OpenCore Bootloader Configuration

* **OpenCore Version:** 1.0.7
* **SMBIOS:** `MacBookPro13,1` (Native Skylake, dual-core, native power management; officially maxes out at Monterey 12.7.6 so Apple Software Update never prompts for incompatible Ventura upgrades)
* **Boot-args:** `-v keepsyms=1 debug=0x100 alcid=3 -igfxdvmt -wegnoegpu unfairgva=1`
* **Windows SMBIOS Protection:** `CustomSMBIOSGuid = True`, `UpdateSMBIOSMode = Custom`. Windows 10 boots completely unmolested with native OEM ACPI tables and an activated OEM license.
* **Graphical Menu:** OpenCanopy activated with customized `GoldenGate` theme featuring modern, high-resolution original designs for Windows 11, official Apple logo, and the authentic Linux Tux Penguin, with full mouse pointer control and a sleek dark slate background. Tapping **Spacebar** toggles auxiliary entries (`Reset NVRAM`).

---

## Repository Structure

```
.
├── EFI/
│   ├── BOOT/
│   │   └── BOOTx64.efi              # OpenCore 1.0.7
│   └── OC/
│       ├── ACPI/
│       │   ├── SSDT-PLUG-DRTNIA.aml # CPU Power Management
│       │   ├── SSDT-EC-USBX-LAPTOP.aml # Fake EC and USB power
│       │   ├── SSDT-PNLF.aml        # Backlight control
│       │   └── SSDT-GPU-DISABLE.aml # dGPU powerdown
│       ├── Drivers/                 # OpenRuntime, OpenHfsPlus, OpenCanopy, ResetNvramEntry
│       ├── Kexts/                   # Lilu, VirtualSMC, WhateverGreen, AppleALC, etc.
│       └── config.plist             # Validated Monterey configuration
├── build_efi.py                     # One-click EFI builder & validator
├── toggle_picker.bat                # Toggle between Graphical and Text bootloader
└── UTBMap.kext                      # Native USB port mapping
```

---

## How to Build / Update the EFI

To reassemble and validate the EFI after making modifications:

```cmd
python build_efi.py
```

This script:
1. Compiles the pristine `config.plist`.
2. Validates the configuration using `ocvalidate` (0 errors).
3. Safely updates the active EFI partition (`Z:\EFI`) without touching Windows (`Z:\EFI\Microsoft`).
4. Generates a deployment ZIP archive.

---

## Credits
- [Acidanthera](https://github.com/acidanthera) for OpenCore, Lilu, WhateverGreen, AppleALC, and VirtualSMC.
- [Mieze](https://github.com/Mieze) for RealtekRTL8111.
- [Dortania](https://dortania.github.io/) for the OpenCore Install Guide.
