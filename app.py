# bot.py
import os
import json
import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client(intents=discord.Intents(message_content=True, messages=True, members=True))
tree = app_commands.CommandTree(client)

def get_file_extension(filename):
    return filename.split(".")[-1]

def replace_special_chars_memegen(string):
    return string.replace("-", "--").replace("_", "__").replace(" ", "_").replace("?", "~q").replace("&", "~a").replace("%", "~p").replace("#", "~h").replace("/", "~s").replace("\"", "''").replace("<", "~l").replace(">", "~g")

def feur_add_count(id):
    try:
        with open("data.json", "r") as f:
            data = json.load(f)
    except:
        data = {}
    if id in data:
        data[id] += 1
    else:
        data[id] = 1
    with open("data.json", "w") as f:
        json.dump(data, f)

@tree.command(name = "nbfeur")
async def nbfeur(interaction, user: discord.User = None):
    """Affiche le nombre de fois que quelqu'un a dit "Feur"

    Parameters
    -----------
    user: discord.User
        L'utilisateur à qui afficher le nombre de fois qu'il a dit "Feur" (par défaut, l'auteur de la commande)
    """
    if user == None:
        user = interaction.author
    try:
        with open("data.json", "r") as f:
            data = json.load(f)
    except:
        data = {}
    if str(user.id) in data:
        await interaction.response.send_message(f"{user} a dit \"Feur\" {data[str(user.id)]} fois")
    else:
        await interaction.response.send_message(f"{user} n'a jamais dit \"Feur\"")

@tree.command(name = "rankfeur")
async def rankfeur(interaction):
    """Affiche le classement des personnes qui ont dit "Feur" le plus de fois"""
    try:
        with open("data.json", "r") as f:
            data = json.load(f)
    except:
        data = {}
    data = sorted(data.items(), key=lambda x: x[1], reverse=True)
    message = ""
    for i in range(len(data)):
        message += f"{i+1}. **{client.get_user(int(data[i][0])).name}** : **{data[i][1]}** fois\n"
    await interaction.response.send_message(message)

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
    await tree.sync(guild=discord.Object(id=344844965765054465))
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    new_line = f"{message.created_at.strftime('%m/%d/%Y, %H:%M')} - {message.author}: {message.content}"
    print(new_line)
    if str(message.channel.id) in os.getenv("CHANNELS_TO_LOG"):
        with open("chat.txt", "a") as f:
            f.write(new_line + "\n")
    if "quoi" in message.content.lower() and not message.author.bot:
        feur_add_count(message.author.id)
        await message.channel.send("Feur", reference=message)

client.run(TOKEN)