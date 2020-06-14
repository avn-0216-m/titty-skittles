import json
import asyncio
import requests
import discord
from discord.ext import commands
from discord.utils import get
import sqlite3

bot = commands.Bot(command_prefix="e!")

database_name = "database.sqlite3"
conn = sqlite3.connect(database_name)
c = conn.cursor()

url = "https://www.aphrodites.shop/product/EACYP/estrofemanddiane35-3monthbundle"

test_url = "https://www.reddit.com" #Reliably does not contain "out of stock" in its response body.

querying_store = False
query_headers = {'user-agent': 'Titty Skittles discord bot'}

print("Getting token.")
token = ""
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
            c.execute("SELECT * FROM Guilds")
            guilds_and_channels = c.fetchall()
            for guild, channel in guilds_and_channels:
                #Get all users for a channel
                c.execute("SELECT user_id FROM Users where guild_id = ?", (guild,))
                try:
                    announcement_channel = bot.get_channel(channel)
                except Exception as e:
                    print("Something went wrong getting channel " + str(channel) + " may be deleted.")
                users = c.fetchall()
                print("Sending announcement in channel " + announcement_channel.name)
                announcement = "HRT is available! 🎉🎉🎉\n"
                for user, in users:
                    try:
                        announcement += bot.get_user(user).mention + "\n"
                    except Exception as e:
                        print("Something went wrong with pinging user" + str(user))
                        #Remove them from the DB here.
                await announcement_channel.send(announcement)
            should_alert = False #Don't alert everyone again.
        else:
            should_alert = True

@bot.command()
async def here(context):
    c.execute("SELECT guild_id FROM Guilds where guild_id = ?", (context.guild.id,))
    guild_id = c.fetchone()
    if guild_id is None:
        #Create
        c.execute("INSERT INTO Guilds(guild_id, channel_id) VALUES(?,?)", (context.guild.id, context.channel.id))
    else:
        #Update
        c.execute("UPDATE Guilds SET channel_id = ? WHERE guild_id = ?", (context.channel.id, context.guild.id))
    
    conn.commit()
    await context.send("Alright, I'll post here if HRT is available. :)")

@bot.command()
async def subscribe(context):

    c.execute("SELECT channel_id FROM Guilds where guild_id = ?", (context.guild.id,))
    channel_id = c.fetchone()
    if channel_id is None: return #Can't subscribe if the bot isn't going to post anything anyway.

    if c.execute("SELECT user_id FROM Users WHERE guild_id = ? AND user_id = ?", (context.guild.id,context.message.author.id)).fetchone() is not None:
        await context.send("You're already subscribed!")
        return

    c.execute("INSERT INTO Users(guild_id, user_id) VALUES(?,?)", (context.guild.id,context.message.author.id))
    conn.commit()

    await context.send("Okay! I'll ping you in this guild if HRT is in stock. :)")

@bot.command()
async def unsubscribe(context):

    c.execute("SELECT channel_id FROM Guilds where guild_id = ?", (context.guild.id,))
    channel_id = c.fetchone()
    if channel_id is None: return #Can't unsubscribe if the bot isn't going to post anything anyway.

    c.execute("DELETE FROM Users WHERE user_id = ? AND guild_id = ?", (context.message.author.id,context.guild.id))
    conn.commit()

    await context.send("Alright, you won't be pinged by me in this guild. :)")


@bot.command()
async def about(context):
    await context.send("""
    Hello! I'm the titty skittles bot. I ping https://www.aphrodites.shop/product/EACYP/estrofemanddiane35-3monthbundle every 15 minutes to see if HRT is available.
    \nUse **e!here** to tell me what text channel you'd like me to post notifications in.
    \nUse **e!subscribe** if you'd like me to ping you when HRT is in stock!
    \nUse **e!unsubscribe** if you no longer want me to ping you about HRT.
    \nThank you for using me~!
    """)

@bot.event
async def on_ready():
    print("Titty skittles bot ready.")
    await bot.change_presence(activity = discord.Game("e!about for info. :)"))
    global querying_store
    if not querying_store:
        querying_store = True
        asyncio.ensure_future(query_store())

@bot.event
async def on_guild_remove(guild):
    #Remove the guild ID from the DB.
    c.execute("DELETE FROM Channels WHERE guild_id = ?", guild.id,)
    conn.commit()


print("Doing migration.")
c.execute("CREATE TABLE IF NOT EXISTS Guilds(guild_id INTEGER PRIMARY KEY NOT NULL, channel_id INTEGER NOT NULL);")
c.execute("CREATE TABLE IF NOT EXISTS Users(guild_id INTEGER NOT NULL, user_id INTEGER NOT NULL, FOREIGN KEY (guild_id) REFERENCES Channels(guild_id));")
conn.commit()
print("Migration done.")

print("Starting bot.")
bot.run(token)