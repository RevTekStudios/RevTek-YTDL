"""Offline integration test: generate a video, serve it, download and convert it."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

from app import ROOT, download_args, downloads_folder


class ConversionTests(unittest.TestCase):
    def test_downloads_folder(self):
        self.assertTrue(downloads_folder().is_absolute())

    def test_invalid_input(self):
        for url in ("", "file:///video.mp4", "--exec=anything", "https://"):
            with self.assertRaises(ValueError):
                download_args(url, "output", "mp3")

    def test_conversion(self):
        ffmpeg = ROOT / ".tools" / "win32" / "ffmpeg.exe"
        ffprobe = ROOT / ".tools" / "win32" / "ffprobe.exe"
        if not ffmpeg.is_file():
            self.skipTest("Run the app once to provision FFmpeg first")
        with tempfile.TemporaryDirectory(dir=ROOT / ".tmp") as temporary:
            work = Path(temporary)
            subprocess.run([str(ffmpeg), "-v", "error", "-f", "lavfi", "-i",
                            "color=c=blue:s=160x120:r=10", "-f", "lavfi", "-i",
                            "sine=frequency=440:duration=1", "-t", "1", "-c:v", "mpeg4",
                            "-c:a", "aac", str(work / "sample.mp4")], check=True)
            server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(work)))
            threading.Thread(target=server.serve_forever, daemon=True).start()
            try:
                for fmt, codec in (("mp3", "mp3"), ("m4a", "aac"), ("wav", "pcm_s16le")):
                    with self.subTest(format=fmt):
                        target = work / fmt
                        args = download_args(f"http://127.0.0.1:{server.server_port}/sample.mp4", str(target), fmt)
                        executable = os.environ.get("TEST_APP_EXE")
                        log_path = work / f"{fmt}.log"
                        command = [executable] if executable else [sys.executable, str(ROOT / "app.py")]
                        env = {**os.environ, "PATH": os.environ.get("SystemRoot", "C:\\Windows") + "\\System32"}
                        result = subprocess.run([*command, "--worker-log", str(log_path), "--verbose", *args],
                                                capture_output=True, text=True, timeout=120, env=env, cwd=work)
                        activity = log_path.read_text(encoding="utf-8") if log_path.exists() else "Missing worker log"
                        self.assertEqual(result.returncode, 0, activity + result.stdout + result.stderr)
                        if executable:
                            self.assertIn("JS runtimes: node-", activity)
                        files = list(target.glob(f"*.{fmt}"))
                        self.assertEqual(len(files), 1)
                        probe = subprocess.check_output([str(ffprobe), "-v", "error", "-show_streams", "-of", "json", str(files[0])])
                        streams = json.loads(probe)["streams"]
                        self.assertEqual([s["codec_type"] for s in streams], ["audio"])
                        self.assertEqual(streams[0]["codec_name"], codec)
            finally:
                server.shutdown()
                server.server_close()


if __name__ == "__main__":
    unittest.main()
