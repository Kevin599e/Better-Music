from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

import yt_dlp


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


def download_audio(query: str, output_dir: Path, audio_format: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "outtmpl": str(output_dir / "%(title).200s [%(id)s].%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_format,
                "preferredquality": "0",
            }
        ],
    }

    target = build_target(query)
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([target])


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
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        download_audio(args.query, Path(args.output), args.format)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
