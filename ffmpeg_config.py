import os
import shutil
from pathlib import Path


def _winget_ffmpeg_dir() -> Path | None:
    packages_dir = Path(os.getenv("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"
    if not packages_dir.exists():
        return None

    matches = sorted(packages_dir.glob("Gyan.FFmpeg*/*/bin/ffmpeg.exe"))
    return matches[-1].parent if matches else None


def _ffmpeg_exe_from_path() -> Path | None:
    found = shutil.which("ffmpeg")
    return Path(found) if found else None


_env_ffmpeg_exe = os.getenv("FFMPEG_EXE")
_env_ffmpeg_dir = os.getenv("FFMPEG_DIR")
_winget_dir = _winget_ffmpeg_dir()

FFMPEG_EXE = (
    Path(_env_ffmpeg_exe)
    if _env_ffmpeg_exe
    else _ffmpeg_exe_from_path() or (_winget_dir / "ffmpeg.exe" if _winget_dir else Path("ffmpeg"))
)

FFMPEG_DIR = Path(_env_ffmpeg_dir) if _env_ffmpeg_dir else (FFMPEG_EXE.parent if FFMPEG_EXE.exists() else None)
