/*
 * Intel ACPI Component Architecture
 * AML/ASL+ Disassembler version 20251212 (32-bit version)
 * Copyright (c) 2000 - 2025 Intel Corporation
 * 
 * Disassembling to symbolic ASL+ operators
 *
 * Disassembly of EFI/OC/ACPI/SSDT-PNLF.aml
 *
 * Original Table Header:
 *     Signature        "SSDT"
 *     Length           0x00000078 (120)
 *     Revision         0x02
 *     Checksum         0x31
 *     OEM ID           "CORP"
 *     OEM Table ID     "PNLF"
 *     OEM Revision     0x00000000 (0)
 *     Compiler ID      "INTL"
 *     Compiler Version 0x20251212 (539300370)
 */
DefinitionBlock ("", "SSDT", 2, "CORP", "PNLF", 0x00000000)
{
    External (_SB_.PCI0.GFX0, DeviceObj)

    Scope (_SB.PCI0.GFX0)
    {
        Device (PNLF)
        {
            Name (_HID, EisaId ("APP0002"))  // _HID: Hardware ID
            Name (_CID, "backlight")  // _CID: Compatible ID
            Name (_UID, 0x10)  // _UID: Unique ID
            Name (_STA, 0x0B)  // _STA: Status
        }
    }
}

