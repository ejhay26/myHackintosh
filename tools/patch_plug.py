import subprocess

iasl = 'tools/SSDTTime/Scripts/iasl.exe'
dsl_path = 'EFI/OC/ACPI/SSDT-PLUG-DRTNIA.dsl'

with open(dsl_path, 'r', encoding='utf-8') as f:
    text = f.read()

target = '    If (CondRefOf (\\_SB.CPU0))'
if target in text:
    parts = text.rsplit('}', 1)
    new_body = parts[0].replace(target, '    If (_OSI ("Darwin"))\n    {\n' + target, 1) + '\n    }\n}'
    with open(dsl_path, 'w', encoding='utf-8') as f:
        f.write(new_body)
    res = subprocess.run([iasl, dsl_path], capture_output=True, text=True)
    print("iasl returncode:", res.returncode)
    if res.returncode == 0:
        print("Compiled successfully!")
    else:
        print(res.stdout)
