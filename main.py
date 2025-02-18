# bot.py
import os
import requests
import discord
import epitran
import json
import signal
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

KUURO_ID = 138729016038391808
DEV_GUILD_ID = 1071519891196223528

async def get_data_old():
    # get data from jsonbin
    # Read data from jsonbin.io
    response = requests.get("https://api.jsonbin.io/v3/b/" + JSONBIN_ID + "/latest", json=None, headers={
        "X-Access-Key": JSONBIN_KEY,
        "X-Bin-Meta": "false"
    })

    return response.json()

def replace_all_data(data):
    # create data folder if not exists
    if not os.path.exists("data"):
        os.makedirs("data")
    try:
        for server in data:
            # create file if not exists
            if not os.path.exists(f"data/{server}.json"):
                with open(f"data/{server}.json", "w") as f:
                    f.write("{}")
            for user in data[server]:
                write_data(server, user, data[server][user])
    except Exception as e:
        print(f"Error while replacing data: {e}")
        for filename in os.listdir("data"):
            os.remove(f"data/{filename}")
        os.rmdir("data")
        exit(1)

def get_data(server_id=None, user_id=None):
    if server_id is None:
        data = {}
        for filename in os.listdir("data"):
            with open(f"data/{filename}", "r") as f:
                data[filename.split(".")[0]] = json.load(f)
        return data
    else:
        with open(f"data/{server_id}.json", "r") as f:
            data = json.load(f)
        if user_id is None:
            return data
        else:
            if str(user_id) in data:
                return data[str(user_id)]
            else:
                return 0

def write_data(server_id, user_id, count):
    with open(f"data/{server_id}.json", "r") as f:
        data = json.load(f)
    data[str(user_id)] = count
    with open(f"data/{server_id}.json", "w") as f:
        json.dump(data, f)

def backup_data():
    # Sauvegarde les données sur jsonbin
    data = get_data()
    headers = {
        "Content-Type": "application/json",
        "X-Access-Key": JSONBIN_KEY
    }
    response = requests.put(f"https://api.jsonbin.io/v3/b/{JSONBIN_ID}", json=data, headers=headers)
    print(response.text)

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
    data = get_data(guild_id, user_id)
    data += 1
    write_data(guild_id, user_id, data)



@tree.command(name = "nbfeur")
async def nbfeur(interaction, user: discord.User = None):
    """Affiche le nombre de fois que quelqu'un s'est fait "Feur"

    Parameters
    -----------
    user: discord.User
        L'utilisateur à qui afficher le nombre de fois qu'il s'est fait "Feur" (par défaut, l'auteur de la commande)
    """
    if user is None:
        user = interaction.user
    if user.bot:
        await interaction.response.send_message(f"Les bots ne peuvent pas se faire {FEUR}", ephemeral=True)
        return
    try:
        data = get_data(interaction.guild_id)
    except IOError:
        data = {}
    if str(user.id) in data:
        await interaction.response.send_message(f"{user.name} s'est fait {FEUR} **{data[str(user.id)]}** fois")
    else:
        await interaction.response.send_message(f"{user.name} n'a jamais été {FEUR}")

@tree.command(name = "rankfeur")
async def rankfeur(interaction):
    """Affiche le classement des personnes qui se sont fait "Feur" le plus de fois"""
    try:
        data = get_data(interaction.guild_id)
    except IOError:
        data = {}
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
    if image is None:
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
    # Get data from jsonbin if data folder doesn't exist (first launch or dyno restart)
    if not os.path.exists("data"):
        print("Data folder doesn't exist, getting saved data from jsonbin...")
        data = await get_data_old()
        replace_all_data(data)
    if PRODUCTION:
        status = "production"
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="quoi ?"))
        #await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="maintenance en cours"))
    else:
        status = "développement"
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="kwa ?"))
    print(f'{client.user} has connected to Discord! ({status})')

@client.event
async def on_message(message):
    if message.author.bot:
        return
    if message.author.id == KUURO_ID:
        try:
            if message.content == "sync_feur_dev":
                print("syncing")
                await tree.sync(guild=discord.Object(id=DEV_GUILD_ID))
                await message.add_reaction("✅")
            if message.content == "sync_feur_all":
                print("syncing")
                await tree.sync()
                await message.add_reaction("✅")
            if message.content == "majbdd_feur":
                data = await get_data_old()
                replace_all_data(data)
                await message.add_reaction("✅")
            if message.content == "backup_feur":
                backup_data()
                await message.add_reaction("✅")
        except Exception as e:
            await message.add_reaction("❌")
            await message.channel.send(e)
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

def signal_handler(sig, frame):
    print("Saving data before exiting...")
    if os.path.exists("data"):
        backup_data()
        exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

client.run(TOKEN)