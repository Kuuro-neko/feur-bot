# bot.py
import os
import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client(intents=discord.Intents(message_content=True, messages=True))
tree = app_commands.CommandTree(client)

def get_file_extension(filename):
    return filename.split(".")[-1]

def replace_special_chars_memegen(string):
    return string.replace("-", "--").replace("_", "__").replace(" ", "_").replace("?", "~q").replace("&", "~a").replace("%", "~p").replace("#", "~h").replace("/", "~s").replace("\"", "''").replace("<", "~l").replace(">", "~g")

@tree.command(name = "memegen")
async def memegen(interaction, image: str, top: str="", bottom: str=""):
    """Génère un meme avec le texte en haut et en bas

    Parameters
    -----------
    top: str
        Texte à afficher en haut de l'image
    
    bottom: str
        Texte à afficher en bas de l'image

    image: str
        Lien vers l'image à utiliser
    """
    if image == None:
        await interaction.response.send_message("Il faut mettre une image")
        return
    ext = get_file_extension(image)
    if ext not in ["jpg", "jpeg", "png", "gif"]:
        await interaction.response.send_message("L'image doit être un jpg, un png ou un gif")
        return
    top = replace_special_chars_memegen(top)
    bottom = replace_special_chars_memegen(bottom)
    await interaction.response.send_message(f"https://api.memegen.link/images/custom/{top}/{bottom}.{ext}?background={image}")

@client.event
async def on_ready():
    await tree.sync()
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    new_line = f"{message.created_at.strftime('%m/%d/%Y, %H:%M')} - {message.author}: {message.content}"
    print(new_line)
    if str(message.channel.id) in os.getenv("CHANNELS_TO_LOG"):
        with open("chat.txt", "a") as f:
            f.write(new_line + "\n")
    if  "quoi" in message.content.lower():
        await message.channel.send("Feur", reference=message)


client.run(TOKEN)