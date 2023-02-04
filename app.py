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

def feur_add_count(user_id, guild_id):
    try:
        with open("data.json", "r") as f:
            data = json.load(f)
    except:
        data = {}
    if str(guild_id) not in data:
        data[str(guild_id)] = {}
    if str(user_id) in data[str(guild_id)]:
        data[str(guild_id)][str(user_id)] += 1
    else:
        data[str(guild_id)][str(user_id)] = 1
    with open("data.json", "w") as f:
        json.dump(data, f)

@tree.command(name = "nbfeur")
async def nbfeur(interaction, user: discord.User = None):
    """Affiche le nombre de fois que quelqu'un s'est fait "Feur"

    Parameters
    -----------
    user: discord.User
        L'utilisateur à qui afficher le nombre de fois qu'il s'est fait "Feur" (par défaut, l'auteur de la commande)
    """
    if user == None:
        user = interaction.user
    guild = interaction.guild_id
    try:
        with open("data.json", "r") as f:
            data = json.load(f)
    except:
        data = {}
    if str(guild) not in data:
        data[str(guild)] = {}
    if str(user.id) in data[str(guild)]:
        await interaction.response.send_message(f"{user.name} s'est fait \"Feur\" **{data[str(guild)][str(user.id)]}** fois")

@tree.command(name = "rankfeur")
async def rankfeur(interaction):
    """Affiche le classement des personnes qui se sont fait "Feur" le plus de fois"""
    guild = interaction.guild_id
    try:
        with open("data.json", "r") as f:
            data = json.load(f)
    except:
        data = {}
    if str(guild) not in data:
        data[str(guild)] = {}
    data = data[str(guild)]
    data = {k: v for k, v in sorted(data.items(), key=lambda item: item[1], reverse=True)}
    message = f"Classement des personnes qui se sont fait \"Feur\" le plus de fois par <@{client.user.id}>:\n\n"
    for i, (user_id, count) in enumerate(data.items()):
        user = await client.fetch_user(user_id)
        message += f"{i+1}. {user.name} - {count} fois\n"
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
    await tree.sync()
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    new_line = f"{message.created_at.strftime('%m/%d/%Y, %H:%M')} - {message.author}: {message.content}"
    print(new_line)
    if str(message.channel.id) in os.getenv("CHANNELS_TO_LOG"):
        with open("chat.txt", "a") as f:
            f.write(new_line + "\n")
    if "quoi" in message.content.lower() and not message.author.bot:
        feur_add_count(message.author.id, message.guild.id)
        await message.add_reaction("🇫")
        await message.add_reaction("🇪")
        await message.add_reaction("🇺")
        await message.add_reaction("🇷")

client.run(TOKEN)