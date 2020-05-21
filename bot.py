import json
import asyncio
import requests
import discord
from discord.ext import commands
from discord.utils import get

bot = commands.Bot(command_prefix="e!")

token = {}

url = "https://www.aphrodites.shop/product/EACYP/estrofemanddiane35-3monthbundle"

test_url = "https://www.reddit.com" #Reliably does not contain "out of stock" in its response body.

querying_store = False

query_headers = {'user-agent': 'Titty Skittles discord bot'}

output_channels = {}
ping_users = {}

print("Getting token.")

with open("bot_token.txt") as file:
    token = file.readline()

async def query_store():
    print("Beginning store query routine.")
    should_alert = True
    while True:
        await asyncio.sleep(60 * 15) #Every 15 minutes.
        response = requests.get(url, headers={'user-agent':'Titty Skittles Discord Bot'})
        print("Store queried.")
        if "out of stock" not in response.text.lower():

            print("Titty skittles in stock!")

            if not should_alert:
                return

            print("Informing everyone!")

            for guild in bot.guilds:
                channel_id = output_channels.get(guild.id, None)
                if channel_id is not None:
                    try:
                        channel = bot.get_channel(channel_id)
                        
                        guild_pings = ping_users.get(guild.id, None)

                        message = "Tity Skittles are available! 🎉🎉🎉"

                        if guild_pings is not None:
                            message += "\n\n"
                            for user_id in guild_pings:
                                try:
                                    message += bot.get_user(user_id).mention
                                except:
                                    print("Couldn't get user.")
                                    pass
                        else:
                            print("No users to ping.")

                        await channel.send(message)

                    except:
                        print(f"Something went wrong with messaging {channel_id}. :(")
                should_alert = False #Wont alert again until 
        else:
            should_alert = True

def load_from_storage():

    with open("guilds.json") as g_json_in:
        output_channels = json.load(g_json_in)

    with open("users.json") as u_json_in:
        ping_users = json.load(u_json_in)

    print("Loaded data:")
    print(output_channels)
    print(ping_users)

    print("Data loaded.")


def persist_storage():

    with open("guilds.json", "w") as g_json_out:
        json.dump(output_channels, g_json_out)

    with open("users.json", "w") as u_json_out:
        json.dump(ping_users, u_json_out)

    print("Data persisted.")

@bot.command()
async def here(context):
    output_channels[context.guild.id] = context.channel.id
    await context.send("Got it! I'll post here if HRT is in stock. :)")

    persist_storage()

@bot.command()
async def subscribe(context):
    await context.send("Okay! I'll ping you if HRT is in stock. :)")
    server_ping_users = ping_users.get(context.guild.id, None)
    if server_ping_users is not None:
        server_ping_users.append(context.message.author.id)
        ping_users[context.guild.id] = server_ping_users
    else:
        server_ping_users = [context.message.author.id]
        ping_users[context.guild.id] = server_ping_users

    print(f"Users to ping in {context.guild.name}:")
    print(server_ping_users)

    persist_storage()

@bot.command()
async def unsubscribe(context):
    await context.send("Alright, you won't be pinged by me. :)")
    server_ping_users = ping_users.get(context.guild.id, None)
    if server_ping_users is not None:
        server_ping_users.remove(context.message.author.id)
        ping_users[context.guild.id] = server_ping_users
    print(f"Users to ping in {context.guild.name}:")
    print(server_ping_users)

    persist_storage()

@bot.command()
async def about(context):

    persist_storage()

    await context.send("""Hello! I'm the titty skittles bot. I ping https://www.aphrodites.shop/product/EACYP/estrofemanddiane35-3monthbundle every 15 minutes to see if HRT is available.
    \nUse **e!here** to tell me what text channel you'd like me to post notifications in.
    \nUse **e!subscribe** if you'd like me to ping you when HRT is in stock!
    \nUse **e!unsubscribe** if you no longer want me to ping you about HRT.
    \nThank you for using me~!""")

@bot.event
async def on_ready():
    print("Titty skittles bot ready.")

    load_from_storage()

    await bot.change_presence(activity = discord.Game("e!about for info. :)"))

    global querying_store
    if not querying_store:
        querying_store = True
        asyncio.ensure_future(query_store())

print("Starting bot.")

bot.run(token)