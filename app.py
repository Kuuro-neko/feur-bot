# bot.py
import os
import json
import discord
import epitran
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client(intents=discord.Intents().all())
tree = app_commands.CommandTree(client)

QUOI_PHONETIQUE = epitran.Epitran("fra-Latn").transliterate("quoi")
KOA_PHONETIQUE = epitran.Epitran("fra-Latn").transliterate("koa")
ALLO_PHONETIQUE = epitran.Epitran("fra-Latn").transliterate("allo")
ALLO_QUESTION_PHONETIQUE = epitran.Epitran("fra-Latn").transliterate("allo ?")[:3]
ALLOI_PHONETIQUE = epitran.Epitran("fra-Latn").transliterate("alloi")[:3]

FEUR = "<:feur:1071522848159567944>"
AL = "<:al:1071535087885234196>"
HUILE = "<:huile:1071533394585985196>"

def get_file_extension(filename):
    return filename.split(".")[-1]

def replace_special_chars_memegen(string):
    return string.replace("-", "--").replace("_", "__").replace(" ", "_").replace("?", "~q").replace("&", "~a").replace("%", "~p").replace("#", "~h").replace("/", "~s").replace("\"", "''").replace("<", "~l").replace(">", "~g")

def feur_add_count(user_id, guild_id):
    try:
        with open("data/data.json", "r") as f:
            data = json.load(f)
    except:
        data = {}
    if str(guild_id) not in data:
        data[str(guild_id)] = {}
    if str(user_id) in data[str(guild_id)]:
        data[str(guild_id)][str(user_id)] += 1
    else:
        data[str(guild_id)][str(user_id)] = 1
    with open("data/data.json", "w") as f:
        json.dump(data, f)

#Command to config the bot (only for administators). Slash commands that takes a feur bool and a allo bool
"""
@tree.command(name = "config")
async def config(interaction, feur: bool = True, allo: bool = True):
    Configure le bot

    Parameters
    -----------
    feur: bool
        Si le bot doit répondre à "feur" (par défaut, True)
    
    allo: bool
        Si le bot doit répondre à "allo" (par défaut, True)
    
    if interaction.user.guild_permissions.administrator:
        try:
            with open("data/config.json", "r") as f:
                data = json.load(f)
        except:
            data = {}
        data[str(interaction.guild_id)] = {"feur": feur, "allo": allo}
        with open("data/config.json", "w") as f:
            json.dump(data, f)
        await interaction.response.send_message("Configuration enregistrée")
    else:
        await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande")
"""

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
        with open("data/data.json", "r") as f:
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
        with open("data/data.json", "r") as f:
            data = json.load(f)
    except:
        data = {}
    if str(guild) not in data:
        data[str(guild)] = {}
    data = data[str(guild)]
    data = {k: v for k, v in sorted(data.items(), key=lambda item: item[1], reverse=True)}
    embed = discord.Embed(title = f"Classement des personnes qui se sont fait {FEUR} le plus de fois", color = 0xABB5BF)
    for i, (user_id, count) in enumerate(data.items()):
        user = await client.fetch_user(user_id)
        embed.add_field(name = "", value = f"{i+1}. **{user.name}** - {count} fois", inline = False)
    await interaction.response.send_message(embed = embed)

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
async def on_guild_join(guild):
    await tree.sync(guild=guild)

@client.event
async def on_ready():
    await tree.sync()
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="quoi ?"))
    print(f'{client.user} has connected to Discord!')

@client.event
async def on_message(message):
    if message.author.bot:
        return
    new_line = f"{message.created_at.strftime('%m/%d/%Y, %H:%M')} - {message.author}: {message.content}"
    message_phonetique = epitran.Epitran("fra-Latn").transliterate(message.content.lower()).replace(" ", "").replace("'", "")
    if str(message.channel.id) in os.getenv("CHANNELS_TO_LOG"):
        with open("chat.txt", "a") as f:
            f.write(new_line + "\n")
    if (QUOI_PHONETIQUE in message_phonetique or KOA_PHONETIQUE in message_phonetique):
        try:
            feur_add_count(message.author.id, message.guild.id)
        except:
            pass
        await message.add_reaction(FEUR)
    
    if (ALLO_PHONETIQUE in message_phonetique or ALLO_QUESTION_PHONETIQUE in message_phonetique or ALLOI_PHONETIQUE in message_phonetique):
        await message.add_reaction(AL)
        await message.add_reaction(HUILE)

client.run(TOKEN)