# RevTek Link2Audio

**[Download for Windows (.exe)](https://github.com/RevTekStudios/RevTek-YTDL/releases/latest/download/Link-to-Audio.exe)** · [All releases](https://github.com/RevTekStudios/RevTek-YTDL/releases)

The published download above may still use the previous Link to Audio name until a new release is published.
The current local build is **RevTek Link2Audio**.

Download the executable and double-click it. No installer, Python, or separate
media tools required. Windows 10/11, 64-bit.

A small Windows desktop app built on yt-dlp. Paste a video URL, choose MP3,
M4A, or WAV, pick a folder, and click **Download audio**. MP3 is the default.
Downloads run in the background with progress, an activity log, and cancellation.
The dark interface includes format cards, a clipboard paste button, and an
expandable activity panel. Press **Ctrl+Enter** to start a download. Errors
automatically reveal the activity log; completion is marked in green.
Playlist links download only the selected video. Files include the title and video
ID, and existing files are not overwritten.

## Run

For the standalone Windows version, double-click **dist/RevTek Link2Audio.exe**.
It contains Python, FFmpeg, FFprobe, and Node.js, so no separate installation
is required. Copy the single executable wherever you want to keep it.
The app extracts its bundled files to a temporary directory while running;
startup can take a few seconds. Internet access is needed for video downloads.
The default save location is your Windows Downloads folder, including any
custom location configured in Windows.

### Run from source

Double-click **Start.cmd**. Python 3.10 or newer with Tkinter must be installed
and available as `python`. The launcher creates a local `.venv` and installs the
Python dependencies. FFmpeg and FFprobe are fetched into `.tools` on the first
download if they are not already on PATH. Internet access is needed for setup
and downloads. The default output folder is your Windows Downloads folder.

For full YouTube support, install Node.js (version 20 or newer) or Deno and make
it available on PATH. The app enables Node and yt-dlp also detects Deno by default.
Some sites may require authentication or reject downloads; this first version
does not expose browser cookies or sign-in settings. Check the activity log for
the reason when a download fails.

MP3 uses yt-dlp's highest variable quality setting. M4A keeps compatible audio
when possible; WAV uses much more disk space. Converting does not improve source
audio quality. Cancelled downloads may leave partial files for later resuming.
Only download content you own or have permission to download.

## Update

For source installations, from PowerShell in this folder:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade -r requirements.txt
```

Rebuild the executable after updating its bundled dependencies.

## Build the executable

Install Node.js on the build machine, then run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe build.py
```

The build creates `dist/RevTek Link2Audio.exe` with the RTS icon. The bundled
media tools make the executable larger, but users only need this one file.
Build tooling: [PyInstaller](https://pyinstaller.org/en/stable/usage.html).

## Verify

After FFmpeg has been provisioned, run:

```powershell
.\.venv\Scripts\python.exe -m unittest -v
```

To test the packaged worker and its bundled tools instead:

```powershell
$env:TEST_APP_EXE = (Resolve-Path '.\dist\RevTek Link2Audio.exe').Path
.\.venv\Scripts\python.exe -m unittest -v
Remove-Item Env:TEST_APP_EXE
```

The test creates a one-second video and serves it on localhost, then downloads
and converts it to all three formats and checks the resulting audio streams.
It does not require an external video service.

References: [yt-dlp documentation](https://github.com/yt-dlp/yt-dlp#readme),
[static-ffmpeg](https://github.com/zackees/static_ffmpeg).

## RTS identity

The interface uses the RevTek Studios folded R mark, Abyss blue-black surfaces,
Ion cyan actions, cool silver text, and consistent semantic status colors. See [BRAND.md](BRAND.md) for the
reusable palette, logo assets, and guidance for future RTS products.
