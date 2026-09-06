import urllib.request
import re
import os
import zipfile

repos = [
    ('Lilu', 'acidanthera/Lilu'),
    ('VirtualSMC', 'acidanthera/VirtualSMC'),
    ('WhateverGreen', 'acidanthera/WhateverGreen'),
    ('AppleALC', 'acidanthera/AppleALC'),
    ('ECEnabler', '1Revenger1/ECEnabler'),
    ('VoodooPS2', 'acidanthera/VoodooPS2'),
    ('RealtekRTL8111', 'Mieze/RTL8111_driver_for_OS_X'),
    ('BrightnessKeys', 'acidanthera/BrightnessKeys'),
]

os.makedirs('tools/kexts', exist_ok=True)
os.makedirs('tools/kexts_extracted', exist_ok=True)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for name, repo in repos:
    latest_url = f'https://github.com/{repo}/releases/latest'
    req = urllib.request.Request(latest_url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            final_url = resp.geturl()
            tag = os.path.basename(final_url)
            print(f'{name} latest tag: {tag}')
            
            assets_url = f'https://github.com/{repo}/releases/expanded_assets/{tag}'
            req_assets = urllib.request.Request(assets_url, headers=headers)
            with urllib.request.urlopen(req_assets) as aresp:
                ahtml = aresp.read().decode('utf-8', errors='ignore')
                links = re.findall(r'href=[\'"](/[^\'"]+/releases/download/[^\'"]+\.zip)[\'"]', ahtml)
                release_links = [l for l in links if '-RELEASE.zip' in l or '-Release.zip' in l]
                chosen = release_links[0] if release_links else (links[0] if links else None)
                if chosen:
                    full_url = f'https://github.com{chosen}'
                    fname = os.path.basename(chosen)
                    dest = os.path.join('tools/kexts', fname)
                    print(f'Downloading {name} (RELEASE) from {full_url}...')
                    urllib.request.urlretrieve(full_url, dest)
                    print(f'Extracting {fname}...')
                    with zipfile.ZipFile(dest, 'r') as zf:
                        zf.extractall(f'tools/kexts_extracted/{name}')
                    print(f'Done {name}')
                else:
                    print(f'No zip found in expanded_assets for {name}')
    except Exception as e:
        print(f'Error for {name}: {e}')
