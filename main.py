# bot.py
import os
import requests
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

JSONBIN_ID = os.getenv("JSONBIN_ID")
JSONBIN_KEY = os.getenv("JSONBIN_KEY")

def get_data():
    # get data from jsonbin
    # Read data from jsonbin.io
    response = requests.get("https://api.jsonbin.io/v3/b/" + JSONBIN_ID + "/latest", json=None, headers={
        "X-Access-Key": JSONBIN_KEY,
        "X-Bin-Meta": "false"
    })

    return response.json()

def write_data(data):
    # Write data to jsonbin.io
    response = requests.put("https://api.jsonbin.io/v3/b/" + JSONBIN_ID, json=data, headers={
        "Content-Type": "application/json",
        "X-Access-Key": JSONBIN_KEY
    })

def to_phonetique(message):
    # Ignorer URL et "alors" (un peu relou de répondre à l'huile à alors)
    message = message.lower()
    message = " ".join([word for word in message.split() if (not word.startswith("http") and not word.startswith("alors") and not word.startswith("www."))])
    return epitran.Epitran("fra-Latn").transliterate(message)

def quoi_in_phonetique(message_phonetique):
    return QUOI_PHONETIQUE in message_phonetique or KOA_PHONETIQUE in message_phonetique

def allo_in_phonetique(message_phonetique):
    return ALLO_PHONETIQUE in message_phonetique or ALLO_QUESTION_PHONETIQUE in message_phonetique or ALLOI_PHONETIQUE in message_phonetique

def get_file_extension(filename):
    return filename.split(".")[-1]

def replace_special_chars_memegen(string):
    return string.replace("-", "--").replace("_", "__").replace(" ", "_").replace("?", "~q").replace("&", "~a").replace("%", "~p").replace("#", "~h").replace("/", "~s").replace("\"", "''").replace("<", "~l").replace(">", "~g")

def feur_add_count(user_id, guild_id):
    data = get_data()
    if str(guild_id) not in data:
        data[str(guild_id)] = {}
    if str(user_id) in data[str(guild_id)]:
        data[str(guild_id)][str(user_id)] += 1
    else:
        data[str(guild_id)][str(user_id)] = 1
    write_data(data)

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
    if user.bot:
        await interaction.response.send_message(f"Les bots ne peuvent pas se faire {FEUR}", ephemeral=True)
        return
    guild = interaction.guild_id
    data = get_data()
    if str(guild) not in data:
        data[str(guild)] = {}
    if str(user.id) in data[str(guild)]:
        await interaction.response.send_message(f"{user.name} s'est fait {FEUR} **{data[str(guild)][str(user.id)]}** fois")
    else:
        await interaction.response.send_message(f"{user.name} n'a jamais été {FEUR}")

@tree.command(name = "rankfeur")
async def rankfeur(interaction):
    """Affiche le classement des personnes qui se sont fait "Feur" le plus de fois"""
    guild = interaction.guild_id
    data = get_data()
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
        Lien vers l'image à utiliser. Le lien doit se terminer par : .png | .jpg | .jpeg | .gif
    """
    if image == None:
        await interaction.response.send_message("Il faut mettre une image")
        return
    ext = get_file_extension(image)
    if ext not in ["jpg", "jpeg", "png", "gif"]:
        await interaction.response.send_message("Le lien de l'image doit se terminer par : .png | .jpg | .jpeg | .gif", ephemeral=True)
        return
    top = replace_special_chars_memegen(top)
    bottom = replace_special_chars_memegen(bottom)
    texte_phonetique = to_phonetique(top + " " + bottom)
    texte_additionnel = ""
    if quoi_in_phonetique(texte_phonetique):
        texte_additionnel += f" {FEUR}"
        feur_add_count(interaction.user.id, interaction.guild_id)
    if allo_in_phonetique(texte_phonetique):
        texte_additionnel += f" {AL}{HUILE}"
    await interaction.response.send_message(f"https://api.memegen.link/images/custom/{top}/{bottom}.{ext}?background={image}")
    if texte_additionnel != "":
        channel = interaction.channel_id
        await client.http.request(discord.http.Route('POST', '/channels/{channel_id}/messages', channel_id=channel), json={"content": texte_additionnel})
    

@client.event
async def on_guild_join(guild):
    await tree.sync(guild=guild)

@client.event
async def on_ready():
    PRODUCTION = bool(int(os.getenv('PRODUCTION')))
    if PRODUCTION:
        status = "production"
        await tree.sync()
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="quoi ?"))
    else:
        status = "développement"
        await tree.sync(guild=discord.Object(id=1071519891196223528))
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="kwa ?"))
    print(f'{client.user} has connected to Discord! ({status})')

@client.event
async def on_message(message):
    if message.author.bot:
        return
    try:
        if message.content[0] == "$": # Pour eviter de feurer les commandes Mudae
            return
    except:
        pass
    message_phonetique = to_phonetique(message.content)
    if quoi_in_phonetique(message_phonetique):
        await message.add_reaction(FEUR)
        feur_add_count(message.author.id, message.guild.id)
    if allo_in_phonetique(message_phonetique):
        await message.add_reaction(AL)
        await message.add_reaction(HUILE)

client.run(TOKEN)