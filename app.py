"""A small desktop frontend for yt-dlp. Run Start.cmd on Windows."""
from __future__ import annotations

import os
from pathlib import Path
import queue
import re
import subprocess
import sys
import threading
import tempfile
import time
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
FORMATS = ("mp3", "m4a", "wav")


def downloads_folder() -> Path:
    """Resolve the Windows Known Folder, including redirected Downloads folders."""
    if os.name == "nt":
        import ctypes
        import uuid
        from ctypes import wintypes
        guid = (ctypes.c_ubyte * 16).from_buffer_copy(uuid.UUID("374de290-123f-4565-9164-39c4925e467b").bytes_le)
        path = ctypes.c_wchar_p()
        shell = ctypes.WinDLL("shell32")
        shell.SHGetKnownFolderPath.argtypes = [ctypes.c_void_p, wintypes.DWORD, wintypes.HANDLE, ctypes.POINTER(ctypes.c_wchar_p)]
        shell.SHGetKnownFolderPath.restype = ctypes.c_long
        if shell.SHGetKnownFolderPath(ctypes.byref(guid), 0, None, ctypes.byref(path)) == 0:
            try:
                return Path(path.value)
            finally:
                ole = ctypes.WinDLL("ole32")
                ole.CoTaskMemFree.argtypes = [ctypes.c_void_p]
                ole.CoTaskMemFree(ctypes.cast(path, ctypes.c_void_p))
    return Path.home() / "Downloads"


def worker_command(args: list[str], log_path: str) -> list[str]:
    prefix = [sys.executable] if getattr(sys, "frozen", False) else [sys.executable, "-u", str(ROOT / "app.py")]
    return [*prefix, "--worker-log", log_path, *args]


def download_args(url: str, folder: str, audio_format: str) -> list[str]:
    parsed = urlsplit(url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Paste a complete http:// or https:// video link.")
    if audio_format not in FORMATS:
        raise ValueError("Choose MP3, M4A, or WAV.")
    return [
        "--ignore-config", "--no-playlist", "--no-colors", "--newline",
        "--no-overwrites", "--windows-filenames", "--trim-filenames", "180",
        "--socket-timeout", "30", "--retries", "3",
        "-f", "bestaudio/best", "--extract-audio", "--audio-format", audio_format,
        "--audio-quality", "0", "--embed-metadata",
        "--progress-template", "download:PROGRESS:%(progress._percent_str)s",
        "-P", folder, "-o", "%(title)s [%(id)s].%(ext)s", "--", url,
    ]


def worker(args: list[str]) -> int:
    import shutil
    bundled = ROOT / "bin"
    args = ["--js-runtimes", f"node:{bundled / 'node.exe'}" if (bundled / "node.exe").is_file() else "node", *args]
    if (bundled / "ffmpeg.exe").is_file():
        args = ["--ffmpeg-location", str(bundled), *args]
    elif not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        print("Preparing FFmpeg (first run may download the tools)…", flush=True)
        from static_ffmpeg.run import get_or_fetch_platform_executables_else_raise, get_platform_dir
        tools_dir = ROOT / ".tools" / Path(get_platform_dir()).name
        tools_dir.mkdir(parents=True, exist_ok=True)
        ffmpeg, _ = get_or_fetch_platform_executables_else_raise(download_dir=str(tools_dir))
        args = ["--ffmpeg-location", str(Path(ffmpeg).parent), *args]
    import yt_dlp
    return yt_dlp.main(args) or 0


def main() -> None:
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    from tkinter.scrolledtext import ScrolledText

    root = tk.Tk()
    root.title("Link to Audio")
    root.geometry("900x820")
    root.minsize(760, 810)
    bg, panel, field = "#10131b", "#191e2b", "#111622"
    text, muted, accent = "#f1f4fc", "#929eb6", "#a99aff"
    root.configure(bg=bg)
    icon = tk.PhotoImage(width=32, height=32)
    icon.put(bg, to=(0, 0, 32, 32))
    for x, height in ((5, 8), (11, 18), (17, 26), (23, 14)):
        icon.put(accent, to=(x, (32-height)//2, x+4, (32+height)//2))
    root.iconphoto(True, icon)
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TFrame", background=bg)
    style.configure("Card.TFrame", background=panel)
    style.configure("TLabel", background=bg, foreground=text, font=("Segoe UI", 10))
    style.configure("Muted.TLabel", foreground=muted)
    style.configure("Card.TLabel", background=panel)
    style.configure("Hint.TLabel", background=panel, foreground=muted, font=("Segoe UI", 9))
    style.configure("TEntry", fieldbackground=field, foreground=text, insertcolor=text,
                    bordercolor="#30394e", lightcolor="#30394e", darkcolor="#30394e", padding=11)
    style.map("TEntry", bordercolor=[("focus", accent)], foreground=[("disabled", muted)])
    style.configure("TButton", font=("Segoe UI", 10), padding=(16, 10),
                    background="#293147", foreground=text, borderwidth=0, focuscolor=accent)
    style.map("TButton", background=[("active", "#35415b"), ("disabled", "#202637")],
              foreground=[("disabled", "#62708a")])
    style.configure("Primary.TButton", background=accent, foreground="#18122f", font=("Segoe UI", 11, "bold"))
    style.map("Primary.TButton", background=[("active", "#bfb3ff"), ("disabled", "#39354f")],
              foreground=[("disabled", "#817a9f")])
    style.configure("Horizontal.TProgressbar", background=accent, troughcolor="#2b3244",
                    borderwidth=0, lightcolor=accent, darkcolor=accent, thickness=6)

    frame = ttk.Frame(root, padding=(32, 22))
    frame.pack(fill="both", expand=True)
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(6, weight=1)
    brand = ttk.Frame(frame)
    brand.grid(row=0, sticky="ew", pady=(0, 20))
    ttk.Label(brand, text="◖)))", foreground=accent, font=("Segoe UI", 19, "bold")).pack(side="left")
    ttk.Label(brand, text="  LINK TO AUDIO", font=("Segoe UI", 11, "bold")).pack(side="left")
    ttk.Label(brand, text="VIDEO → AUDIO", style="Muted.TLabel", font=("Segoe UI", 9)).pack(side="right")
    hero = ttk.Frame(frame)
    hero.grid(row=1, sticky="ew", pady=(0, 22))
    ttk.Label(hero, text="Keep the sound.", font=("Segoe UI", 29, "bold")).pack(anchor="w")
    ttk.Label(hero, text="Your favorite videos, ready to listen. Just paste a link and make it yours.",
              style="Muted.TLabel").pack(anchor="w", pady=(5, 0))

    card = ttk.Frame(frame, style="Card.TFrame", padding=22)
    card.grid(row=2, sticky="ew")
    card.columnconfigure(0, weight=1)
    ttk.Label(card, text="01   ADD YOUR LINK", style="Card.TLabel", font=("Segoe UI", 9, "bold")).grid(sticky="w")
    link_row = ttk.Frame(card, style="Card.TFrame")
    link_row.grid(row=1, sticky="ew", pady=(12, 7))
    link_row.columnconfigure(0, weight=1)
    url = tk.StringVar()
    entry = ttk.Entry(link_row, textvariable=url, font=("Segoe UI", 11))
    entry.grid(row=0, column=0, sticky="ew")
    def paste():
        try:
            url.set(root.clipboard_get().strip())
            entry.focus_set()
        except tk.TclError:
            status.set("Clipboard is empty. Copy a video link first.")
    paste_button = ttk.Button(link_row, text="Paste link", command=paste)
    paste_button.grid(row=0, column=1, padx=(10, 0))
    ttk.Label(card, text="A complete video URL · One video per download", style="Hint.TLabel").grid(row=2, sticky="w")
    ttk.Label(card, text="02   CHOOSE YOUR SOUND", style="Card.TLabel", font=("Segoe UI", 9, "bold")).grid(row=3, sticky="w", pady=(22, 12))
    formats_row = ttk.Frame(card, style="Card.TFrame")
    formats_row.grid(row=4, sticky="ew")
    fmt = tk.StringVar(value="mp3")
    format_buttons = []
    for col, (value, description) in enumerate((("mp3", "Plays everywhere"), ("m4a", "Small & efficient"), ("wav", "Uncompressed"))):
        formats_row.columnconfigure(col, weight=1, uniform="format")
        button = tk.Radiobutton(formats_row, text=f"{value.upper()}\n{description}", variable=fmt,
                                value=value, indicatoron=False, bg=field, fg=muted,
                                selectcolor="#39314f", activebackground="#39314f", activeforeground=text,
                                disabledforeground="#59637a", font=("Segoe UI", 10),
                                relief="flat", bd=0, highlightthickness=1, highlightbackground="#30394e",
                                highlightcolor=accent, cursor="hand2", pady=12, takefocus=True)
        button.grid(row=0, column=col, sticky="ew", padx=(0 if col == 0 else 5, 0 if col == 2 else 5))
        format_buttons.append(button)
    def highlight_format(*_):
        for value, button in zip(FORMATS, format_buttons):
            button.configure(fg=text if fmt.get() == value else muted)
    fmt.trace_add("write", highlight_format)
    highlight_format()
    ttk.Label(card, text="03   SAVE SOMEWHERE GOOD", style="Card.TLabel", font=("Segoe UI", 9, "bold")).grid(row=5, sticky="w", pady=(22, 12))
    destination = ttk.Frame(card, style="Card.TFrame")
    destination.grid(row=6, sticky="ew")
    destination.columnconfigure(0, weight=1)
    folder = tk.StringVar(value=str(downloads_folder()))
    folder_entry = ttk.Entry(destination, textvariable=folder, font=("Segoe UI", 10))
    folder_entry.grid(row=0, column=0, sticky="ew")
    def browse():
        chosen = filedialog.askdirectory(initialdir=folder.get() if Path(folder.get()).is_dir() else ROOT)
        if chosen:
            folder.set(chosen)
    browse_button = ttk.Button(destination, text="Browse…", command=browse)
    browse_button.grid(row=0, column=1, padx=(10, 0))
    actions = ttk.Frame(frame)
    actions.grid(row=3, sticky="ew", pady=(18, 18))

    status_card = ttk.Frame(frame, style="Card.TFrame", padding=(18, 14))
    status_card.grid(row=4, sticky="ew")
    status_card.columnconfigure(0, weight=1)
    status = tk.StringVar(value="Ready when you are")
    badge = tk.StringVar(value="READY")
    ttk.Label(status_card, textvariable=status, style="Card.TLabel").grid(row=0, column=0, sticky="w")
    badge_label = ttk.Label(status_card, textvariable=badge, background=panel, foreground=accent, font=("Segoe UI", 9, "bold"))
    badge_label.grid(row=0, column=1, padx=(12, 0))
    progress = ttk.Progressbar(status_card, maximum=100)
    progress.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(12, 0))

    details = ttk.Frame(frame)
    details.grid(row=5, sticky="ew", pady=(10, 4))
    details_visible = tk.BooleanVar(value=False)
    def toggle_details():
        details_visible.set(not details_visible.get())
        if details_visible.get():
            log.grid()
            root.geometry(f"{root.winfo_width()}x{min(max(root.winfo_height(), 950), root.winfo_screenheight() - 80)}")
        else:
            log.grid_remove()
        details_button.configure(text="Hide activity −" if details_visible.get() else "Show activity +")
    details_button = ttk.Button(details, text="Show activity +", command=toggle_details)
    details_button.pack(side="left")
    ttk.Label(details, text="Best available source quality", style="Muted.TLabel", font=("Segoe UI", 9)).pack(side="right")
    log = ScrolledText(frame, height=4, font=("Consolas", 9), wrap="word", state="disabled",
                       bg=field, fg=muted, insertbackground=text, relief="flat", bd=0, padx=12, pady=10)
    log.grid(row=6, sticky="nsew", pady=(4, 8))
    log.grid_remove()
    footer = ttk.Frame(frame)
    footer.grid(row=7, sticky="ew", pady=(8, 0))
    ttk.Label(footer, text="Made for listening.", foreground=accent, font=("Segoe UI", 9)).pack(side="left")
    ttk.Label(footer, text="Download only content you own or have permission to use.",
              style="Muted.TLabel", font=("Segoe UI", 8)).pack(side="right")
    events = queue.Queue()
    process = None
    cancelled = False

    def append(text):
        log.configure(state="normal")
        log.insert("end", text + "\n")
        log.see("end")
        log.configure(state="disabled")

    def set_busy(busy):
        for widget in (entry, folder_entry, browse_button, paste_button, start_button, *format_buttons):
            widget.configure(state="disabled" if busy else "normal")
        cancel_button.configure(state="normal" if busy else "disabled")

    def read_output(child, log_path):
        try:
            with open(log_path, encoding="utf-8", errors="replace") as stream:
                while True:
                    line = stream.readline()
                    if line:
                        events.put(("line", line.rstrip()))
                    elif child.poll() is not None:
                        break
                    else:
                        time.sleep(0.1)
            events.put(("done", child.wait()))
        except Exception as exc:
            events.put(("line", str(exc)))
            events.put(("done", 1))
        finally:
            Path(log_path).unlink(missing_ok=True)

    def start():
        nonlocal process, cancelled
        try:
            if not folder.get().strip():
                raise ValueError("Choose a destination folder.")
            target = Path(folder.get()).expanduser().resolve()
            args = download_args(url.get().strip(), str(target), fmt.get())
            target.mkdir(parents=True, exist_ok=True)
            cancelled = False
            with tempfile.NamedTemporaryFile(prefix="link-to-audio-", suffix=".log", delete=False) as output:
                log_path = output.name
            process = subprocess.Popen(
                worker_command(args, log_path),
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True,
                encoding="utf-8", errors="replace", env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                start_new_session=os.name != "nt",
            )
        except (ValueError, OSError) as exc:
            messagebox.showerror("Could not start", str(exc))
            return
        log.configure(state="normal")
        log.delete("1.0", "end")
        log.configure(state="disabled")
        badge.set("WORKING")
        badge_label.configure(foreground=accent)
        progress["value"] = 0
        progress.configure(mode="indeterminate")
        progress.start(12)
        status.set("Getting video information…")
        set_busy(True)
        threading.Thread(target=read_output, args=(process, log_path), daemon=True).start()

    def cancel():
        nonlocal cancelled
        if process and process.poll() is None:
            cancelled = True
            status.set("Cancelling…")
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                               capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                import signal
                os.killpg(process.pid, signal.SIGTERM)

    def open_folder():
        target = Path(folder.get()).expanduser().resolve()
        target.mkdir(parents=True, exist_ok=True)
        os.startfile(target) if os.name == "nt" else subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", str(target)])

    start_button = ttk.Button(actions, text="↓  Download audio", command=start, style="Primary.TButton")
    start_button.pack(side="left")
    cancel_button = ttk.Button(actions, text="Cancel", command=cancel, state="disabled")
    cancel_button.pack(side="left", padx=8)
    ttk.Button(actions, text="Open folder", command=open_folder).pack(side="right")

    def poll():
        nonlocal process
        while not events.empty():
            kind, value = events.get_nowait()
            if kind == "done":
                process = None
                set_busy(False)
                progress.stop()
                progress.configure(mode="determinate")
                badge.set("CANCELLED" if cancelled else "SAVED" if value == 0 else "FAILED")
                badge_label.configure(foreground=muted if cancelled else "#82dbb2" if value == 0 else "#ff9baf")
                if value != 0 and not cancelled and not details_visible.get():
                    toggle_details()
                status.set("Cancelled · Partial files can be resumed by trying again." if cancelled else
                           "Audio saved · Open the folder to listen." if value == 0 else
                           "Download failed · See activity for details.")
                if value == 0 and not cancelled:
                    progress["value"] = 100
            elif value.startswith("PROGRESS:"):
                match = re.search(r"([\d.]+)%", value)
                if match:
                    progress.stop()
                    progress.configure(mode="determinate")
                    progress["value"] = float(match[1])
                    status.set(f"Downloading audio · {match[1]}%")
            else:
                append(value)
                if "[ExtractAudio]" in value:
                    badge.set("CONVERTING")
                    progress.configure(mode="indeterminate")
                    progress.start(12)
                    status.set("Converting audio…")
        root.after(100, poll)

    def close():
        if process and process.poll() is None:
            if not messagebox.askyesno("Download running", "Cancel this download and close?"):
                return
            cancel()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", close)
    root.bind("<Control-Return>", lambda event: start() if process is None else None)
    entry.focus_set()
    poll()
    root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--worker", "--worker-log"):
        args = sys.argv[2:]
        if sys.argv[1] == "--worker-log":
            sys.stdout = sys.stderr = open(args[0], "w", encoding="utf-8", buffering=1)
            args = args[1:]
        try:
            sys.exit(worker(args))
        except Exception as exc:
            print(f"ERROR: {exc}", flush=True)
            sys.exit(1)
    else:
        main()
