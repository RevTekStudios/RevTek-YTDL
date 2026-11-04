"""Build the standalone Windows app using the project's local tools."""
from pathlib import Path
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def main():
    os.chdir(ROOT)
    temporary = ROOT / ".tmp"
    temporary.mkdir(exist_ok=True)
    os.environ["TEMP"] = os.environ["TMP"] = str(temporary)
    from PIL import Image, ImageDraw
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    image = Image.new("RGBA", (256, 256), (16, 19, 27, 255))
    draw = ImageDraw.Draw(image)
    for x, height in ((40, 64), (88, 144), (136, 208), (184, 112)):
        draw.rounded_rectangle((x, (256-height)//2, x+28, (256+height)//2), radius=14, fill="#a99aff")
    image.save(assets / "app.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    tools = ROOT / ".tools" / "win32"
    if not all((tools / name).is_file() for name in ("ffmpeg.exe", "ffprobe.exe")):
        from static_ffmpeg.run import get_or_fetch_platform_executables_else_raise
        get_or_fetch_platform_executables_else_raise(download_dir=str(tools))
    node = shutil.which("node")
    if not node:
        raise SystemExit("Install Node.js before building; its runtime is bundled into the executable.")
    command = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onefile", "--windowed",
               "--name", "Link to Audio", "--icon", str(assets / "app.ico"),
               "--collect-all", "yt_dlp", "--collect-all", "yt_dlp_ejs",
               "--exclude-module", "PIL", "--exclude-module", "twine",
               "--add-binary", f"{tools / 'ffmpeg.exe'}:bin",
               "--add-binary", f"{tools / 'ffprobe.exe'}:bin",
               "--add-binary", f"{node}:bin", "app.py"]
    subprocess.run(command, check=True)
    print(f"Built {ROOT / 'dist' / 'Link to Audio.exe'}")


if __name__ == "__main__":
    main()
