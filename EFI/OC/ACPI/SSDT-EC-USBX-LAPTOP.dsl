DefinitionBlock ("", "SSDT", 2, "DRTNIA", "SsdtEC", 0x00001000)
{
    External (_SB_.PCI0.LPC_.EC__, DeviceObj)
    External (_SB_.PCI0.LPCB.EC__, DeviceObj)

    If ((!CondRefOf (\_SB.PCI0.LPCB.EC) && !CondRefOf (\_SB.PCI0.LPC.EC)))
    {
        Scope (\_SB)
        {
            Device (EC)
            {
                Name (_HID, "ACID0001")
                Method (_STA, 0, NotSerialized)
                {
                    If (_OSI ("Darwin"))
                    {
                        Return (0x0F)
                    }
                    Else
                    {
                        Return (Zero)
                    }
                }
            }
        }
    }

    Device (USBX)
    {
        Name (_ADR, Zero)
        Method (_DSM, 4, NotSerialized)
        {
            If (!_OSI ("Darwin"))
            {
                Return (Buffer (One)
                {
                     0x00
                })
            }

            If ((Arg2 == Zero))
            {
                Return (Buffer (One)
                {
                     0x03
                })
            }

            Return (Package (0x08)
            {
                "kUSBSleepPowerSupply", 
                0x13EC, 
                "kUSBSleepPortCurrentLimit", 
                0x0834, 
                "kUSBWakePowerSupply", 
                0x13EC, 
                "kUSBWakePortCurrentLimit", 
                0x0834
            })
        }
    }
}
