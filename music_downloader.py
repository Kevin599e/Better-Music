from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

import yt_dlp


FFMPEG_LOCATION = Path(
    r"C:\Users\kevin\AppData\Local\Microsoft\WinGet\Packages"
    r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-8.1.1-full_build\bin"
)

SPOTIFY_RE = re.compile(r"https?://open\.spotify\.com/(?:intl-[a-z]{2}/)?(?:track|album|playlist)/[A-Za-z0-9]+")
YOUTUBE_RE = re.compile(r"https?://(?:www\.)?(?:youtube\.com|youtu\.be)/\S+")


def spotify_title(url: str) -> str:
    """Return a searchable title for a public Spotify URL."""
    request = Request(
        f"https://open.spotify.com/oembed?url={quote_plus(url)}",
        headers={"User-Agent": "music-downloader/1.0"},
    )

    with urlopen(request, timeout=15) as response:
        payload = json.loads(response.read().decode("utf-8"))

    title = payload.get("title")
    if not title:
        raise ValueError("Spotify did not return a title for that link.")

    return title


def build_target(query: str) -> str:
    if YOUTUBE_RE.match(query):
        return query

    if SPOTIFY_RE.match(query):
        title = spotify_title(query)
        return f"ytsearch1:{title} audio"

    return f"ytsearch1:{query}"


def resolve_info(target: str, ydl_opts: dict) -> dict:
    with yt_dlp.YoutubeDL({**ydl_opts, "quiet": True, "skip_download": True}) as ydl:
        info = ydl.extract_info(target, download=False)

    if "entries" in info:
        entries = [entry for entry in info["entries"] if entry]
        if not entries:
            raise ValueError("No matching audio result was found.")
        return entries[0]

    return info


def expected_output_path(info: dict, output_dir: Path, audio_format: str) -> Path:
    outtmpl = str(output_dir / "%(title).200s [%(id)s].%(ext)s")
    with yt_dlp.YoutubeDL({"outtmpl": outtmpl, "quiet": True}) as ydl:
        source_path = Path(ydl.prepare_filename(info))

    return source_path.with_suffix(f".{audio_format}")


def find_existing_output(info: dict, output_dir: Path, audio_format: str) -> Path | None:
    final_path = expected_output_path(info, output_dir, audio_format)
    if final_path.exists():
        return final_path

    video_id = info.get("id")
    if not video_id:
        return None

    matches = sorted(output_dir.glob(f"* [{video_id}].{audio_format}"))
    return matches[0] if matches else None


def build_ydl_options(output_dir: str | Path, audio_format: str) -> dict:
    output_dir = Path(output_dir)
    return {
        "format": "bestaudio/best",
        "noplaylist": True,
        "outtmpl": str(output_dir / "%(title).200s [%(id)s].%(ext)s"),
        "overwrites": False,
        "ffmpeg_location": str(FFMPEG_LOCATION),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_format,
                "preferredquality": "0",
            }
        ],
    }


def download_audio(query: str, output_dir: str | Path, audio_format: str = "mp3", force: bool = False) -> Path:
    """Download audio if needed and return the final audio file path."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    ydl_opts = build_ydl_options(output_dir, audio_format)
    target = build_target(query)
    info = resolve_info(target, ydl_opts)
    expected_path = expected_output_path(info, output_dir, audio_format)
    existing_path = find_existing_output(info, output_dir, audio_format)

    if existing_path and not force:
        print(f"Already downloaded: {existing_path}")
        print("Use --force to download it again.")
        return existing_path

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([info.get("webpage_url") or target])

    return find_existing_output(info, output_dir, audio_format) or expected_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Download audio from a YouTube link, a YouTube search title, or a "
            "Spotify music link resolved to a matching public YouTube result."
        )
    )
    parser.add_argument("query", help="Song title, YouTube link, or Spotify music link")
    parser.add_argument(
        "-o",
        "--output",
        default="downloads",
        help="Folder to write audio files into. Default: downloads",
    )
    parser.add_argument(
        "-f",
        "--format",
        default="mp3",
        choices=["mp3", "m4a", "opus", "wav", "flac"],
        help="Audio format to extract. Default: mp3",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Download again even if the expected output file already exists.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        output_path = download_audio(args.query, Path(args.output), args.format, args.force)
        print(f"Audio file: {output_path}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
