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
    from brand import create_assets
    assets = ROOT / "assets"
    create_assets(assets)
    tools = ROOT / ".tools" / "win32"
    if not all((tools / name).is_file() for name in ("ffmpeg.exe", "ffprobe.exe")):
        from static_ffmpeg.run import get_or_fetch_platform_executables_else_raise
        get_or_fetch_platform_executables_else_raise(download_dir=str(tools))
    node = shutil.which("node")
    if not node:
        raise SystemExit("Install Node.js before building; its runtime is bundled into the executable.")
    command = [sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--onefile", "--windowed",
               "--name", "RevTek Link2Audio", "--icon", str(assets / "app.ico"),
               "--add-data", f"{assets / 'app-icon.png'}:assets",
               "--add-data", f"{ROOT / 'design' / 'rts-tokens.json'}:design",
               "--collect-all", "yt_dlp", "--collect-all", "yt_dlp_ejs",
               "--exclude-module", "PIL", "--exclude-module", "twine",
               "--add-binary", f"{tools / 'ffmpeg.exe'}:bin",
               "--add-binary", f"{tools / 'ffprobe.exe'}:bin",
               "--add-binary", f"{node}:bin", "app.py"]
    subprocess.run(command, check=True)
    print(f"Built {ROOT / 'dist' / 'RevTek Link2Audio.exe'}")


if __name__ == "__main__":
    main()
