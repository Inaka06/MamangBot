import discord
from discord.ext import commands
import nltk
from nltk.chat.util import Chat
import yt_dlp
import asyncio
import discord.opus

chatcanda = [
    (r'halo mang|halo mank|halo mamang|halo mamank|mamang|mank|mang|ngab|mamank', ['Yoi?', 'Naon?', 'Ha?', 'Hadir']),
    (r'absen|siapa yang', ['Saya bang!', 'Saya!', 'Aku bang!', 'Aku!']),
    (r'test|tes|coba', ['Berhasil']),
    (r'(.*)', ['Gapaham'])
]

chatbot = Chat(chatcanda, nltk.chat.util.reflections)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

voice = None

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="&helpmank"))
    print(f'{bot.user} sudah nyambung!')

queue = []

@bot.event
async def on_message(message):
    global voice, queue

    if message.author == bot.user:
        return

    if message.content.startswith('&helpmank'):
        await message.channel.send('https://anotepad.com/notes/g9sebmgb')

    if message.content.startswith('&musikmank'):
        url = message.content.split(' ')[1]

        if message.author.voice:
            if not message.guild.voice_client:
                await message.author.voice.channel.connect()
            voice = discord.utils.get(bot.voice_clients, guild=message.guild)
        else:
            await message.channel.send("Ente mana?")
            return

        try:
            ytdl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'audio.mp3',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }]
            }
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                source = discord.FFmpegPCMAudio(info['url'])
                title = info['title']
        except Exception as e:
            await message.channel.send(f"Error: {e}")
            return
        
        queue.append((source, title))
        if len(queue) > 0:
            await message.channel.send(f"{title} masuk antrian.")
        
        def play_next_song(error):
            if error:
                print(f"Error: {error}")
            if len(queue) > 0:
                next_song = queue.pop(0)
                source, title = next_song
                voice.play(source, after=play_next_song)
                asyncio.run_coroutine_threadsafe(message.channel.send(f"Memutar: {title}"), bot.loop) 

        if not voice.is_playing() and len(queue) > 0:
            next_song = queue.pop(0)
            source, title = next_song
            voice.play(source, after=play_next_song)
            asyncio.run_coroutine_threadsafe(message.channel.send(f"Memutar: {title}"), bot.loop)

        while voice.is_playing():
            await asyncio.sleep(1)
        
    if message.content.startswith('&dcmank'):
        voice = discord.utils.get(bot.voice_clients, guild=message.guild)
        if voice and voice.is_playing():
            voice.stop()
            queue = []
            await message.channel.send('Oke, dadah!')
            await voice.disconnect()
        elif voice:
            await voice.disconnect()
            await message.channel.send("Dadah!")
        else:
            await message.channel.send('Disconnect?')

    elif message.content.startswith('&skipmank'):
        voice = discord.utils.get(bot.voice_clients, guild=message.guild)
        if voice and voice.is_playing():
            voice.stop()
            queue.pop(0)
            if queue:
                source, title = queue[0]
                voice.play(source)
                await message.channel.send(f"Memutar: {title}")
            else:
                await message.channel.send('Antrian dah kosong.')
        else:
            await message.channel.send('Skip apaan?')

    if message.content.startswith('&listmank'):
        if len(queue) > 0:
            list_judul = [f"{i+1}. {judul[1]}" for i, judul in enumerate(queue)]
            output_string = '\n'.join(list_judul)
            await message.channel.send(output_string)
        else:
            await message.channel.send('List musik kosong')
            
    if message.content.startswith('&sekarangmank'):
        await message.channel.send(f'Sekarang lagi main {judul[1]}' for judul in(queue))

    elif not message.content.startswith(bot.command_prefix):
        response = chatbot.respond(message.content)
        if response != 'Gapaham':
            await message.channel.send(response)

    await bot.process_commands(message)

bot.run("MTA4MDQ4NzQxNzYxMTU2NzE5Nw.G8f_6Y.8Hwnaghu2CQJ9WuQDGwzg8AZW9u2E1907Us4NU")