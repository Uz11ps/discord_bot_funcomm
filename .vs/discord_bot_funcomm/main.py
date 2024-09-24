import discord
import json
from discord.ext import commands

config_path = 'C:/Users/1/Desktop/discord_bot_funcomm/config.json'
with open('config.json', 'r') as file:
    config = json.load(file)

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix=config['prefix'], intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user.name} ({bot.user.id})')

@bot.command(name='ping')
async def ping(ctx):
    await ctx.send(f'{ctx.author.mention} pong')

bot.run(config['token'])