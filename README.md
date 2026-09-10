# Lenovo Ideapad 300-14ISK Hackintosh (macOS Ventura)

[![OpenCore](https://img.shields.io/badge/OpenCore-1.0.7-blue.svg)](https://github.com/acidanthera/OpenCorePkg)
[![macOS](https://img.shields.io/badge/macOS-Ventura%2013.x-brightgreen.svg)](https://www.apple.com/macos/ventura/)
[![Architecture](https://img.shields.io/badge/Architecture-Intel%20Skylake-orange.svg)](https://ark.intel.com/content/www/us/en/ark/products/88193/intel-core-i5-6200u-processor-3m-cache-up-to-2-80-ghz.html)

A bare-metal OpenCore EFI configuration tailored for the **Lenovo Ideapad 300-14ISK**

---

## Hardware Specifications

| Component | Hardware Specification | Hackintosh Status |
| :--- | :--- | :--- |
| **Model** | Lenovo Ideapad 300-14ISK (Type 80Q6) | Supported |
| **CPU** | Intel Core i5-6200U (2 cores, 4 threads, 2.3 GHz - 2.8 GHz) | Native via `SSDT-PLUG-DRTNIA` (`plugin-type=1`) |
| **iGPU** | Intel HD Graphics 520 (Skylake GT2, Device ID `0x1916`) | Full QE/CI Metal acceleration via OCLC root patches, 2048 MB VRAM |
| **RAM** | 16 GB DDR3L-1600 MHz (Dual-Channel) | Supported |
| **Storage** | Kingston SA400S37240G 240GB SATA SSD | Dual-boot: Windows 10 (152 GB) + macOS (70 GB APFS) |
| **Display (Custom)** | **14.0" 1600x900 HD+ (`CMN14A3` / N140FGE-EA2)** *(Upgraded from stock 1366x768)* | Fully working with native brightness slider & Fn keys |
| **Audio** | Conexant CX20751/2 (`14F1:510F`) | Working via `AppleALC.kext` (`alcid=3`) |
| **Ethernet** | Realtek RTL8168/8111 PCI Gigabit Ethernet (Rev `0x15`) | Working via `RealtekRTL8111.kext` v2.4.2 |
| **Wi-Fi / BT** | Realtek RTL8723B (USB/PCIe Internal) | Requires Wireless-USB-Adapter package |
| **Touchpad** | Synaptics PS/2 Touchpad (`ACPI\SYN2B58`) | Gestures working via `VoodooPS2Controller.kext` |
| **Keyboard** | Standard PS/2 Laptop Keyboard | Working via `VoodooPS2Keyboard.kext` + `BrightnessKeys.kext` |
| **Battery** | Lenovo Dual-Cell / Embedded Controller | Working via `ECEnabler.kext` + `SMCBatteryManager.kext` |

---

## Custom Display Upgrade: 1600x900 (`CMN14A3`)

The factory Lenovo Ideapad 300-14ISK shipped with a low-resolution 1366x768 panel (`LGD04C7`). Replacing the display with a **1600x900 panel (`CMN14A3`)** causes standard Skylake EFI configurations to fail (verbose text scrolls, followed by a permanent black screen). 

### How This EFI Fixes the Replaced Screen:
1. **Direct EDID Injection (`AAPL00,override-no-connect`)**:
   - Extracted the exact 128-byte EDID for `CMN14A3` directly from the hardware registry and injected it into `DeviceProperties` -> `PciRoot(0x0)/Pci(0x2,0x0)`. This allows `AppleIntelSKLGraphicsFramebuffer` to properly synchronize display timings.
2. **Dual-Link Bus Bandwidth (`@0,display-dual-link = <01 00 00 00>`)**:
   - Enables dual-link pixel clock bandwidth (107.8 MHz) required for horizontal resolutions >= 1600px.
3. **Native Skylake Backlight Modulation (`SSDT-PNLF.aml`)**:
   - Injects `PNLF` properly nested inside `_SB.PCI0.GFX0` with `_UID = 0x10` (PWM frequency `0x56C`), allowing `AppleIntelPanel` to hook into the display.
4. **Backlight PWM Restoration (`-igfxblr` + `enable-backlight-registers-fix`)**:
   - Prevents the Intel graphics driver from powering down the PWM duty cycle (`0xC8250`) on boot and wake.
5. **Backlight Smoothing (`enable-backlight-smoother` + `applbkl=1`)**:
   - Enables smooth brightness level stepping and eliminates backlight flicker.
6. **2048 MB VRAM Allocation (`framebuffer-unifiedmem = <00 00 00 80>`)**:
   - Increases WindowServer compositing memory from the default 1536 MB to 2048 MB for buttery-smooth animations.

---

## Audio & Apple Music Optimization

* **Codec:** Conexant CX20751/2 driven by `AppleALC.kext` layout `3`.
* **Apple Music FairPlay DRM:** Intel iGPU-only systems lack hardware FairPlay 2.x/3.x decryption engines. To prevent song skipping:
  - `unfairgva=4` is injected into `boot-args`, allowing the FairPlay pipeline to decrypt music streams smoothly.
  - In Apple Music preferences, select **Lossless (up to 24-bit/48 kHz)**. The internal Conexant DAC supports up to 48 kHz / 24-bit.
  - For Hi-Res Lossless (96 kHz / 192 kHz), connect an external USB DAC.

---

## OpenCore Bootloader Features

* **Version:** OpenCore 1.0.7 (DEBUG/RELEASE validated).
* **Graphical Interface:** OpenCanopy activated with high-definition `Acidanthera\GoldenGate` icons and wireless mouse cursor support.
* **Streamlined OS Menu (`HideAuxiliary = True`):**
  - Displays **only** installed OSes (`Macintosh HD` and `Windows 10`).
  - Automatically displays incoming USB drives (such as **Ventoy**, macOS installers, Linux USBs).
  - Tapping **Spacebar** instantly toggles auxiliary entries (`Reset NVRAM`, Recovery).
* **Native UEFI Boot Priority:** Windows Boot Manager is directed to chainload OpenCore, ensuring the laptop boots straight into the menu without pressing F12.

---

## Utilities & Maintenance

This repository includes custom utilities to manage your Hackintosh from Windows:

| Utility | Location | Description |
| :--- | :--- | :--- |
| **`toggle_picker.bat`** | Repository Root | One-click script to toggle OpenCore between **Graphical** and **Text** mode directly from Windows. |
| **`build_efi.py`** | Repository Root | Python script to assemble, validate, and package the EFI tree. |
| **`fetch_kexts.py`** | `tools/` | Automated script to pull and extract the latest Acidanthera kexts. |

### Switching Bootloader Modes from Windows:
If you ever want to switch between Graphical and Text bootloader modes:
1. In Windows, right-click `toggle_picker.bat` and click **Run as administrator**.
2. The script mounts the internal SSD EFI, toggles `PickerMode`, and unmounts automatically.

---

## Dual-Boot Partition Layout (240GB Kingston SSD)

```
[ Disk 0 (Kingston SA400S37240G) ]
 ├── Partition 1: EFI System Partition (1.0 GB, FAT32)  -> OpenCore 1.0.7 + Windows Boot Manager
 ├── Partition 2: Windows 10 C: (152.6 GB, NTFS)        -> Windows OS (~30.5 GB free for dev)
 └── Partition 3: macOS Ventura (70.0 GB, APFS)         -> Macintosh HD
```

---

## OCLC (OpenCore Legacy Patcher) — Required for Ventura

macOS Ventura dropped native Skylake iGPU Metal support. **OCLC must be run after every clean install or macOS update** to re-inject Skylake GPU kexts:

1. Boot macOS Ventura (even if display is in software-rendered fallback mode)
2. Download [OpenCore Legacy Patcher](https://github.com/dortania/OpenCore-Legacy-Patcher/releases)
3. Run → **Post Install Root Patch** → Apply
4. Reboot

Without OCLC patches: no Metal, no GPU acceleration, apps will be slow/crash.
With OCLC patches: full Metal, smooth animations, Apple Music Lossless works.

*Note: Windows paging file is capped at 2048 MB - 4096 MB at `C:\pagefile.sys` to preserve SSD space for development.*

---

## License & Credits
- [Acidanthera](https://github.com/acidanthera) for OpenCore, Lilu, WhateverGreen, AppleALC, and VirtualSMC.
- [Mieze](https://github.com/Mieze) for RealtekRTL8111.
- [Dortania](https://dortania.github.io/) for the OpenCore Install Guide.
