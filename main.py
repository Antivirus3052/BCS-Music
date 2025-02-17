import os
import platform
import discord
from discord.ext import commands
import yt_dlp
import asyncio
import json
from discord.ui import Button, View, Select
from dotenv import load_dotenv

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

if platform.system() == "Windows":
    FFMPEG_PATH = os.path.join(PROJECT_ROOT, 'ffmpeg', 'bin', 'ffmpeg.exe')
else:
    # Unter Linux nutzen wir in der Regel die systemweite FFmpeg-Installation
    FFMPEG_PATH = '/usr/bin/ffmpeg'

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Update the ydl_opts dictionary
ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'noplaylist': True,  # Only download single songs, not playlists
    'quiet': True,  # Less console spam
    'ffmpeg_location': FFMPEG_PATH  # Add this line
}

load_dotenv()

class MusicPlayer:
    def __init__(self):
        self.queue = []
        self.playing = False
        self.current_song = None
        self.current_song_info = None
        self.load_favorites()

    def load_favorites(self):
        try:
            with open('favorites.json', 'r') as f:
                self.favorites = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.favorites = {}
            self.save_favorites()

    def save_favorites(self):
        with open('favorites.json', 'w') as f:
            json.dump(self.favorites, f, indent=4)

    def add_favorite(self, user_id, song_url, song_title):
        if str(user_id) not in self.favorites:
            self.favorites[str(user_id)] = []
        if song_url not in [song['url'] for song in self.favorites[str(user_id)]]:
            self.favorites[str(user_id)].append({
                'url': song_url,
                'title': song_title
            })
            self.save_favorites()
            return True
        return False

    async def play_next(self, ctx):
        if len(self.queue) > 0:
            self.current_song = self.queue.pop(0)
            voice_client = ctx.voice_client
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(self.current_song, download=False)
                    url = info['url']
                    self.current_song_info = {
                        'title': info.get('title', 'Unknown'),
                        'url': self.current_song,
                        'thumbnail': info.get('thumbnail', None),
                        'duration': info.get('duration', 0)
                    }
                    try:
                        voice_client.play(
                            discord.FFmpegPCMAudio(
                                url, 
                                executable=FFMPEG_PATH
                            ),
                            after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), bot.loop)
                        )
                        self.playing = True
                        await self.update_player_message(ctx)
                    except Exception as e:
                        await ctx.send(f"Error playing audio: {str(e)}")
                        self.playing = False
                        self.current_song = None
            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")
                self.playing = False
                self.current_song = None
        else:
            self.playing = False
            self.current_song = None
            self.current_song_info = None
            await self.update_player_message(ctx)

    async def update_player_message(self, ctx):
        if hasattr(self, 'player_message'):
            try:
                await self.player_message.edit(embed=self.create_player_embed(), view=MusicControlPanel(self))
            except discord.NotFound:
                self.player_message = await ctx.send(embed=self.create_player_embed(), view=MusicControlPanel(self))

    def create_player_embed(self):
        embed = discord.Embed(title="🎵 Music Player", color=discord.Color.blue())
        
        if self.current_song_info:
            embed.add_field(
                name="Now Playing",
                value=f"[{self.current_song_info['title']}]({self.current_song_info['url']})",
                inline=False
            )
            if self.current_song_info['thumbnail']:
                embed.set_thumbnail(url=self.current_song_info['thumbnail'])
        else:
            embed.add_field(name="Now Playing", value="Nothing playing", inline=False)

        queue_text = ""
        for i, song in enumerate(self.queue[:5], 1):
            queue_text += f"{i}. {song}\n"
        embed.add_field(name="Queue", value=queue_text or "Empty", inline=False)
        
        return embed

class MusicControlPanel(View):
    def __init__(self, music_player):
        super().__init__(timeout=None)
        self.music_player = music_player

    @discord.ui.button(label="Play/Pause", emoji="⏯️", style=discord.ButtonStyle.primary)
    async def play_pause(self, interaction: discord.Interaction, button: Button):
        if interaction.guild.voice_client:
            if interaction.guild.voice_client.is_paused():
                interaction.guild.voice_client.resume()
                await interaction.response.send_message("▶️ Resumed", ephemeral=True)
            else:
                interaction.guild.voice_client.pause()
                await interaction.response.send_message("⏸️ Paused", ephemeral=True)

    @discord.ui.button(label="Skip", emoji="⏭️", style=discord.ButtonStyle.primary)
    async def skip(self, interaction: discord.Interaction, button: Button):
        if interaction.guild.voice_client and interaction.guild.voice_client.is_playing():
            interaction.guild.voice_client.stop()
            await interaction.response.send_message("⏭️ Skipped", ephemeral=True)

    @discord.ui.button(label="Stop", emoji="🛑", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button: Button):
        if interaction.guild.voice_client:
            self.music_player.queue.clear()
            interaction.guild.voice_client.stop()
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("🛑 Stopped", ephemeral=True)

    @discord.ui.button(label="Add to Favorites", emoji="❤️", style=discord.ButtonStyle.success)
    async def add_favorite(self, interaction: discord.Interaction, button: Button):
        if self.music_player.current_song_info:
            if self.music_player.add_favorite(
                interaction.user.id,
                self.music_player.current_song_info['url'],
                self.music_player.current_song_info['title']
            ):
                await interaction.response.send_message("❤️ Added to favorites!", ephemeral=True)
            else:
                await interaction.response.send_message("Already in favorites!", ephemeral=True)
        else:
            await interaction.response.send_message("No song is currently playing!", ephemeral=True)

    @discord.ui.select(
        placeholder="Volume Control",
        options=[
            discord.SelectOption(label="10%", value="0.1"),
            discord.SelectOption(label="25%", value="0.25"),
            discord.SelectOption(label="50%", value="0.5"),
            discord.SelectOption(label="75%", value="0.75"),
            discord.SelectOption(label="100%", value="1.0"),
        ]
    )
    async def volume_select(self, interaction: discord.Interaction, select: Select):
        if interaction.guild.voice_client:
            interaction.guild.voice_client.source.volume = float(select.values[0])
            await interaction.response.send_message(f"🔊 Volume set to {int(float(select.values[0])*100)}%", ephemeral=True)

music_player = MusicPlayer()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command()
async def play(ctx, url):
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel!")
        return

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    music_player.queue.append(url)
    
    if not music_player.playing:
        await music_player.play_next(ctx)
        # Fix: Changed MusicControls to MusicControlPanel
        controls = MusicControlPanel(music_player)
        await ctx.send("Now playing! Use the controls below:", view=controls)
    else:
        await ctx.send("Added to queue!")

# Add these new commands
@bot.command()
async def panel(ctx):
    """Display the music control panel"""
    music_player.player_message = await ctx.send(
        embed=music_player.create_player_embed(),
        view=MusicControlPanel(music_player)
    )

@bot.command()
async def favorites(ctx):
    """Show your favorite songs"""
    user_favorites = music_player.favorites.get(str(ctx.author.id), [])
    if not user_favorites:
        await ctx.send("You don't have any favorite songs!")
        return

    embed = discord.Embed(title="Your Favorite Songs", color=discord.Color.pink())
    for i, song in enumerate(user_favorites, 1):
        embed.add_field(
            name=f"{i}. {song['title']}",
            value=f"[Link]({song['url']})",
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command()
async def playfav(ctx, number: int):
    """Play a song from your favorites"""
    user_favorites = music_player.favorites.get(str(ctx.author.id), [])
    if not user_favorites:
        await ctx.send("You don't have any favorite songs!")
        return

    if number < 1 or number > len(user_favorites):
        await ctx.send("Invalid song number!")
        return

    song = user_favorites[number-1]
    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    music_player.queue.append(song['url'])
    
    if not music_player.playing:
        await music_player.play_next(ctx)
    else:
        await ctx.send(f"Added {song['title']} to queue!")

# Replace 'YOUR_BOT_TOKEN' with your actual Discord bot token
bot.run(os.getenv('DISCORD_TOKEN'))