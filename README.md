<<<<<<< HEAD
# Simple Music Downloader (STANDALONE)

This is a small command-line program that accepts:

- A YouTube music link
- A song title/search phrase
- A Spotify music link

It downloads the best available public audio result through `yt-dlp` and extracts it with FFmpeg. Spotify links are used only for metadata lookup, then matched to a public YouTube result; the program does not rip Spotify streams.

Use this only for audio you own, created, have permission to download, or that is otherwise lawful to save.

## Setup

Install Python 3.10 or newer, then install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Install FFmpeg and make sure it is available on your `PATH`:

```powershell
winget install Gyan.FFmpeg
```

For the discord bot set up
Create a api_token.txt file and add your discord bot API key.


Run the application via
```powershell
python .\discordThing.py
```
## Examples via Terminal

Download by title:

```powershell
python music_downloader.py "Daft Punk Around the World"
```

Download from YouTube:

```powershell
python music_downloader.py "https://www.youtube.com/watch?v=example"
```

Download using a Spotify track link as the search source:

```powershell
python music_downloader.py "https://open.spotify.com/track/example"
```

Choose a format and output folder:

```powershell
python music_downloader.py "song title" --format flac --output "C:\Music"
```

Downloaded files are saved to `downloads` by default.
=======
# Better-Music

This section explains the discord functionality of the application. 

## Whats currently implemented?

Search and Download Music

## Example command

Download by Search
```
$download fly me to the moon

```
Download by Youtube Link

```
$download https://www.youtube.com/watch?v=5cUq9qgez5w
```


 
