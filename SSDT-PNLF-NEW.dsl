DefinitionBlock ("", "SSDT", 2, "CORP", "PNLF", 0x00000000)
{
    External (_SB_.PCI0.GFX0, DeviceObj)

    Scope (_SB.PCI0.GFX0)
    {
        Device (PNLF)
        {
            Name (_HID, EisaId ("APP0002"))
            Name (_CID, "backlight")
            Name (_UID, 0x10) // 16: Skylake / Kaby Lake (PWM Max 0x56c)
            Name (_STA, 0x0B)
        }
    }
}
