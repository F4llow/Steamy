from dataclasses import asdict
import discord
from discord.ext import commands, tasks
from discord.utils import get
import asyncio
from steam import Steam

#####################################################################################################

intents = discord.Intents.all()

client = commands.Bot(command_prefix = "!", intents = intents)

TOKEN = "MTA5MTQ3MjkzMTkyMzcxMDA4Mw.GUfV9b.zEGS7OPhJ11KYP9vhfh_pbHuyXTRjKv0QgmSNA"

#####################################################################################################

STEAM_KEY = "753D25017221CF96C6D14701B7B4752C"

steam = Steam(STEAM_KEY)

#####################################################################################################

testDB = {}

supportedAchievements = [976730]

@client.event
async def on_ready():
    print("The bot is online.")
    await notification.start()

@client.event
async def on_member_join(member):
    await member.send("Welcome!")

@client.command()
async def setID(ctx, *, ID):
    testDB[ctx.message.author] = steam.users.search_user(ID)["player"]["steamid"]
    await ctx.send(str(ctx.message.author) + ": " + testDB[ctx.message.author])

@client.command()
async def database1(ctx):
    for i in testDB:
        print(i, testDB[i], "\n")

@client.command()
async def achievements(ctx):
    list = []
    max = 0
    for i in testDB:
        count = 0
        id = testDB[i]
        all = steam.apps.get_user_achievements(id, "976730")["playerstats"]["achievements"]
        for j in all:
            if j["achieved"] == 1:
                count += 1
        list.append((id, count))
    #bubble sort the list of tuples to order largest to smallest by the second index in the tuple
    n = len(list)
    for j in range(n):
        for k in range(n - 1):
            if list[k][1] < list[k + 1][1]:
                list[k], list[k + 1] = list[k + 1], list[k]
    await ctx.send(steam.users.get_user_details(list[0][0])["player"]["personaname"] + " has " + str(list[0][1]) + " achievements for first place.")
    await ctx.send(steam.users.get_user_details(list[1][0])["player"]["personaname"] + " has " + str(list[1][1]) + " achievements for second place.")

@client.command()
async def searchUser(ctx):
    id = testDB[ctx.message.author]
    account = steam.users.get_user_details(id)
    await ctx.send(account)

@client.command()
async def userDetails(ctx):
    id = testDB[ctx.message.author]
    steamID = steam.users.search_user(id)["player"]["steamid"]
    #account = steam.users.get_user_details(id)[0]
    await ctx.send(steamID)

@client.command()
async def game(ctx, *, game):
    id = steam.apps.search_games(game)["apps"][0]["id"]
    await ctx.send(id)

#####################################################################################################

notifyDB = {}

@client.command()
async def notify(ctx, *, game):
    title = steam.apps.search_games(game)
    nameSS = title["apps"][0]["name"]
    id = title["apps"][0]["id"]
    price = title["apps"][0]["price"]
    member = ctx.message.author
    nameS = nameSS + " Notification"
    if nameSS not in notifyDB.keys():
        notifyDB[nameSS] = [nameSS, id, price]
        await ctx.guild.create_role(name = nameS)
    else:
        await ctx.send("There are already notifications for this game. You will now recieve notifications.")
    role = get(member.guild.roles, name = nameS)
    await member.add_roles(role)
    await ctx.send(nameSS)
    await ctx.send(id)
    await ctx.send(price)

@client.command()
async def database2(ctx):
    for i in notifyDB:
        print(i, notifyDB[i], "\n")
        await ctx.send("The database will appear in your console.")

@tasks.loop(seconds = 5)
async def notification():
    channel = await client.fetch_channel(1091852415134871692)
    if len(notifyDB) == 0:
        #await channel.send("There are no games in the notification database.")
        pass
    else:
        for i in notifyDB:
            cost = steam.apps.search_games(notifyDB[i][0])["apps"][0]["price"]
            if notifyDB[i][2] > cost:
                await channel.send("@" + notifyDB[i][0] + " Notification" + " has decreased from " + str(notifyDB[i][2]) + " to " + str(cost))
            else:
                continue

@notification.before_loop
async def start_loop():
    await client.wait_until_ready()

#####################################################################################################

@client.command()
async def leaderSpeedrun(ctx):
    # sends leaderboard of speedrun if the game has time achievements

    pass

@client.command()
async def leaderPlaytime(ctx):
    # sends leaderboard of how many hours server participants have played of a given game
    pass

@client.command()
async def coOp(ctx):
    # Adds users to a queue of individuals that want to play coop of a specific game.
    # If there's two people within the same server that want to play a specific game together,
    # the bot will create a voice chat and add both users to it.
    pass

#####################################################################################################

client.run(TOKEN)
