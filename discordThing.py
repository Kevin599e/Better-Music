# This example requires the 'message_content' intent.

import sys
from pathlib import Path
from collections import deque
import discord
import music_downloader
import music_player


intents = discord.Intents.default()
intents.message_content = True
default_dir = Path(__file__).parent / "downloads"
client = discord.Client(intents=intents)
queue = deque() # FiFO queue 
#                            HELPER FUNCTIONS                                #
#============================================================================#
def getFilePath(query):
    return music_downloader.download_audio(query, default_dir)

async def downloadFunc(message):
        disc_query = message.content.removeprefix("$download ").strip() #strips the mesasge does by removing $download for the query
        print(f"Searching for audio {disc_query}")
        await message.channel.send(f"Searching for {disc_query}")
        try:
            file_path = getFilePath(disc_query) # Sets the file path to the file. If it exists then it doesn't download the audio file.
        except Exception as exc:
            print(f"Error: {exc}", file=sys.stderr)
            await message.channel.send(f"Error: {exc}")
            return

        if file_path.exists():
            print(f"{disc_query} Found")
            try:
                await message.channel.send(file=discord.File(file_path))
                await message.channel.send(f"Enjoy :wink:")
            except Exception as exc:
                print(f"Send error: {exc}", file=sys.stderr)
                await message.channel.send(f"Downloaded it, but Discord could not send the file: {exc}")
        else:
            await message.channel.send(f"Could not find file: {file_path}")

async def playSong(message):
     disc_query = message.content.removeprefix("$play ").strip()
     file_path = getFilePath(disc_query)
     await music_player.play_file(message, file_path)

    
async def pause(message):
    await music_player.pause(message)

async def resume(message):
    await music_player.resume(message)
#============================================================================#

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    print(f"Downloads folder: {default_dir}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")

    if message.content.startswith("$download"):
        await downloadFunc(message)

    if message.content.startswith("$play"):
        await playSong(message)

    if message.content.startswith("$pause"):
        await pause(message)

    if message.content.startswith("$resume"):
        await resume(message)


client.run(Path("api_token.txt").read_text().strip())
