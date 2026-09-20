import os
import sys
import io
import struct
import subprocess
from PIL import Image, ImageDraw

WORKSPACE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

def pack_icns(img_256: Image.Image, img_128: Image.Image) -> bytes:
    """Packs 128x128 and 256x256 PNG images into an Apple ICNS container with ic07 and ic13 chunks."""
    b_128 = io.BytesIO()
    img_128.save(b_128, format="PNG")
    data_128 = b_128.getvalue()
    
    b_256 = io.BytesIO()
    img_256.save(b_256, format="PNG")
    data_256 = b_256.getvalue()
    
    chunk_128 = b"ic07" + struct.pack(">I", len(data_128) + 8) + data_128
    chunk_256 = b"ic13" + struct.pack(">I", len(data_256) + 8) + data_256
    
    body = chunk_128 + chunk_256
    header = b"icns" + struct.pack(">I", len(body) + 8)
    return header + body

def create_windows_11_logo() -> Image.Image:
    """Generates the official vibrant Azure Blue Windows 11 4-square grid logo."""
    # 256x256 transparent canvas
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Official Microsoft Windows 11 Azure Blue
    win_blue = (0, 120, 215, 255) # #0078D7
    
    # Geometry: 4 squares centered with 12px gap
    total_size = 176
    gap = 12
    sq_size = (total_size - gap) // 2 # 82px
    start_x = (256 - total_size) // 2 # 40px
    start_y = (256 - total_size) // 2 # 40px
    radius = 3 # subtle rounded modern corners
    
    # Top-Left
    draw.rounded_rectangle([start_x, start_y, start_x + sq_size, start_y + sq_size], radius=radius, fill=win_blue)
    # Top-Right
    draw.rounded_rectangle([start_x + sq_size + gap, start_y, start_x + total_size, start_y + sq_size], radius=radius, fill=win_blue)
    # Bottom-Left
    draw.rounded_rectangle([start_x, start_y + sq_size + gap, start_x + sq_size, start_y + total_size], radius=radius, fill=win_blue)
    # Bottom-Right
    draw.rounded_rectangle([start_x + sq_size + gap, start_y + sq_size + gap, start_x + total_size, start_y + total_size], radius=radius, fill=win_blue)
    
    return img

def create_apple_logo() -> Image.Image:
    """Renders the authentic Apple silhouette logo in clean platinum white (#F5F5F7)."""
    svg_data = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 170 170" width="170" height="170">
  <path fill="#F5F5F7" d="M150.37 130.25c-2.45 5.66-5.35 10.87-8.71 15.66-4.58 6.53-8.33 11.05-11.22 13.56-4.48 4.12-9.28 6.23-14.42 6.35-3.69 0-8.14-1.05-13.32-3.18-5.19-2.12-9.97-3.17-14.34-3.17-4.58 0-9.49 1.05-14.74 3.17-5.26 2.13-9.5 3.24-12.74 3.35-4.35.13-9.16-1.9-14.42-6.08-3.7-3.04-7.58-7.7-11.64-13.98-6.19-9.5-10.9-19.78-14.13-30.84-3.23-11.06-4.85-21.78-4.85-32.17 0-14.44 3.7-26.6 11.09-36.48 7.39-9.88 16.74-14.93 28.05-15.15 4.35 0 9.42 1.25 15.22 3.75 5.8 2.5 9.77 3.8 11.91 3.9 1.95 0 6.08-1.42 12.38-4.25 6.3-2.83 11.75-4.14 16.34-3.94 13.06.63 23.44 5.37 31.14 14.22-11.77 7.15-17.54 16.89-17.3 29.21.24 9.94 4.14 18.28 11.71 25.02 7.56 6.74 16.48 10.59 26.74 11.55-2.09 6.24-4.66 12.83-7.72 19.78zm-30.82-108.97c0 6.55-2.42 12.82-7.25 17.81-4.83 4.99-10.66 8.01-17.49 9.06-.52-2.19-.78-4.22-.78-6.09 0-6.44 2.65-12.85 7.95-18.24 5.3-5.39 11.6-8.52 18.9-9.39.13 2.15.19 4.43.19 6.85z"/>
</svg>"""
    html_path = os.path.join(WORKSPACE, "tools", "temp_apple.html")
    png_path = os.path.join(WORKSPACE, "tools", "temp_apple.png")
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 256px; height: 256px; background: transparent; overflow: hidden; display: flex; align-items: center; justify-content: center; }}
svg {{ width: 180px; height: 180px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3)); }}
</style>
</head>
<body>
{svg_data}
</body>
</html>"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    cmd = [
        BRAVE_PATH,
        "--headless",
        "--disable-gpu",
        "--default-background-color=00000000",
        "--window-size=256,256",
        f"--screenshot={png_path}",
        html_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    
    img = Image.open(png_path).convert("RGBA")
    
    if os.path.exists(html_path):
        os.remove(html_path)
    if os.path.exists(png_path):
        os.remove(png_path)
        
    return img

def extract_caddy() -> Image.Image:
    """Extracts the GoldenGate external drive caddy frame from ExtHardDrive.icns."""
    ehd_path = os.path.join(WORKSPACE, "tools", "OcBinaryData", "Resources", "Image", "Acidanthera", "GoldenGate", "ExtHardDrive.icns")
    hd_path = os.path.join(WORKSPACE, "tools", "OcBinaryData", "Resources", "Image", "Acidanthera", "GoldenGate", "HardDrive.icns")
    
    # Let's read ic13 from ExtHardDrive
    def get_png(path):
        with open(path, "rb") as f:
            data = f.read()
        offset = 8
        while offset < len(data):
            tag, chunk_size = struct.unpack(">4sI", data[offset:offset+8])
            chunk_data = data[offset+8:offset+chunk_size]
            if tag == b"ic13" and chunk_data.startswith(b"\x89PNG"):
                return Image.open(io.BytesIO(chunk_data)).convert("RGBA")
            offset += chunk_size
        return None

    ext_hd = get_png(ehd_path)
    return ext_hd

def make_external_variant(icon_256: Image.Image, caddy_256: Image.Image) -> Image.Image:
    """Composites an OS logo scaled onto the external drive caddy frame."""
    # Scale OS icon down slightly to fit nicely on the caddy
    icon_scaled = icon_256.resize((170, 170), Image.Resampling.LANCZOS)
    canvas = caddy_256.copy()
    # Paste centered horizontally, slightly offset vertically
    offset_x = (256 - 170) // 2
    offset_y = (256 - 170) // 2 - 12
    canvas.paste(icon_scaled, (offset_x, offset_y), icon_scaled)
    return canvas

def main():
    print("=== Generating Authentic Modern OS Icons for OpenCanopy ===")
    
    # 1. Windows 11 Azure Blue
    win_256 = create_windows_11_logo()
    win_128 = win_256.resize((128, 128), Image.Resampling.LANCZOS)
    win_icns = pack_icns(win_256, win_128)
    print("Windows 11 Azure Blue icon generated successfully.")
    
    # 2. Apple Pure Platinum White / Silver
    apple_256 = create_apple_logo()
    apple_128 = apple_256.resize((128, 128), Image.Resampling.LANCZOS)
    apple_icns = pack_icns(apple_256, apple_128)
    print("Official Apple icon generated successfully.")
    
    # 3. Linux Tux Penguin (from existing Linux.icns or create)
    # Let's get the 256x256 Tux from tools/OcBinaryData if present or current Linux.icns
    linux_icns_path = os.path.join(WORKSPACE, "EFI", "OC", "Resources", "Image", "Acidanthera", "GoldenGate", "Linux.icns")
    if os.path.exists(linux_icns_path):
        with open(linux_icns_path, "rb") as f:
            linux_icns = f.read()
    else:
        linux_icns = apple_icns # fallback
        
    # 4. External Variants
    caddy = extract_caddy()
    if caddy:
        ext_win_256 = make_external_variant(win_256, caddy)
        ext_win_128 = ext_win_256.resize((128, 128), Image.Resampling.LANCZOS)
        ext_win_icns = pack_icns(ext_win_256, ext_win_128)
        
        ext_apple_256 = make_external_variant(apple_256, caddy)
        ext_apple_128 = ext_apple_256.resize((128, 128), Image.Resampling.LANCZOS)
        ext_apple_icns = pack_icns(ext_apple_256, ext_apple_128)
        
        # ExtLinux
        ext_linux_path = os.path.join(WORKSPACE, "EFI", "OC", "Resources", "Image", "Acidanthera", "GoldenGate", "ExtLinux.icns")
        if os.path.exists(ext_linux_path):
            with open(ext_linux_path, "rb") as f:
                ext_linux_icns = f.read()
        else:
            ext_linux_icns = ext_apple_icns
    else:
        ext_win_icns = win_icns
        ext_apple_icns = apple_icns
        ext_linux_icns = linux_icns

    # Targets to deploy:
    # 1. tools/OcBinaryData/Resources/Image/Acidanthera/GoldenGate
    # 2. EFI/OC/Resources/Image/Acidanthera/GoldenGate
    # 3. Z:\EFI\OC\Resources\Image\Acidanthera\GoldenGate (if mounted)
    targets = [
        os.path.join(WORKSPACE, "tools", "OcBinaryData", "Resources", "Image", "Acidanthera", "GoldenGate"),
        os.path.join(WORKSPACE, "EFI", "OC", "Resources", "Image", "Acidanthera", "GoldenGate")
    ]
    if os.path.exists("Z:\\EFI\\OC\\Resources\\Image\\Acidanthera\\GoldenGate"):
        targets.append("Z:\\EFI\\OC\\Resources\\Image\\Acidanthera\\GoldenGate")
        
    icon_map = {
        "Windows.icns": win_icns,
        "ExtWindows.icns": ext_win_icns,
        "Apple.icns": apple_icns,
        "ExtApple.icns": ext_apple_icns,
        "Linux.icns": linux_icns,
        "ExtLinux.icns": ext_linux_icns,
    }
    
    for t in targets:
        os.makedirs(t, exist_ok=True)
        for fname, data in icon_map.items():
            dest = os.path.join(t, fname)
            with open(dest, "wb") as f:
                f.write(data)
            print(f"Deployed {fname} ({len(data)} bytes) to {dest}")

    print("=== All Modern OS Icons Deployed Successfully! ===")

if __name__ == "__main__":
    main()
