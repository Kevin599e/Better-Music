from pathlib import Path
import asyncio

import discord

from ffmpeg_config import FFMPEG_EXE


async def join_vc(message) -> discord.VoiceClient:
    if message.author.voice is None:
        await message.channel.send("You are not in a voice channel silly")
        return None
    v_channel = message.author.voice.channel
    if message.guild.voice_client is not None:
        return message.guild.voice_client
    return await v_channel.connect()

def make_audio_source(file_path: Path) -> discord.AudioSource:
    return discord.FFmpegPCMAudio(str(file_path), executable=str(FFMPEG_EXE))

async def play_file(message, file_path: Path) -> None:
    if not file_path.exists():
        await message.channel.send("Audio file was not found")
        return
    
    voice_client = message.guild.voice_client
    if voice_client is None:
        voice_client = await join_vc(message)
    if voice_client is None:
        print(f"Bot failed to join target VC")
        return
    if voice_client.is_playing():
        voice_client.stop()
    
    source = make_audio_source(file_path)
    voice_client.play(source)

    await message.channel.send(f"Now playing: '{file_path.name}'")

async def disconnect(message) -> None:
    voice_client = message.guild.voice_client
    if voice_client is None:
        await message.channel.send("No voice channel to disconnect")
        return None
    
    await voice_client.disconnect()
    await message.channel.send("Disconnected from the voice channel")

