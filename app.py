# bot.py
import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
print(type(TOKEN))
client = discord.Client(intents=discord.Intents(message_content=True, messages=True))

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if  "quoi" in message.content.lower():
        await message.channel.send("Feur", reference=message)

client.run(TOKEN)