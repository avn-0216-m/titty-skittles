import asyncio
import requests
import discord
from discord.ext import commands
from discord.utils import get

bot = commands.Bot(command_prefix="e!")

token = {}

url = "https://www.aphrodites.shop/product/EACYP/estrofemanddiane35-3monthbundle"

querying_store = False

query_headers = {'user-agent': 'Titty Skittles discord bot'}

output_channels = {}
ping_users = {}

print("Getting token.")

with open("bot_token.txt") as file:
    token = file.readline()

async def query_store():
    print("Beginning store query routine.")
    while True:
        await asyncio.sleep(60 * 15) #Every 15 minutes.
        response = requests.get(url, headers={'user-agent':'Titty Skittles Discord Bot'})
        print("Store queried.")
        if "out of stock" not in response.text.lower():
            print("Titty skittles in stock!")
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


@bot.command()
async def here(context):
    output_channels[context.guild.id] = context.channel.id
    await context.send("Got it! I'll post here if HRT is in stock. :)")

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

@bot.command()
async def unsubscribe(context):
    await context.send("Alright, you won't be pinged by me. :)")
    server_ping_users = ping_users.get(context.guild.id, None)
    if server_ping_users is not None:
        server_ping_users.remove(context.message.author.id)
        ping_users[context.guild.id] = server_ping_users
    print(f"Users to ping in {context.guild.name}:")
    print(server_ping_users)

@bot.event
async def on_ready():
    print("Titty skittles bot ready.")
    global querying_store
    if not querying_store:
        querying_store = True
        asyncio.ensure_future(query_store())

print("Starting bot.")

bot.run(token)