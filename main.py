import os
import dbHandler
import discord
from discord.ext import commands

from steam.webapi import WebAPI
from dotenv import load_dotenv

load_dotenv()
STEAMWEBKEY = os.getenv('STEAMWEBKEY')
DISCORDTOKEN = os.getenv('DISCORD_TOKEN')
#use .env for this....
api = WebAPI(key= STEAMWEBKEY)

dbHandler.initDB()

intents = discord.Intents.default()
intents.members = False

bot = commands.Bot(command_prefix='?', intents=intents)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def add(ctx, vanity: str):
    print (api.ISteamWebAPIUtil.GetServerInfo())
    vanity_dict = api.ISteamUser.ResolveVanityURL(vanityurl=vanity)
    steam_ID = (vanity_dict['response']["steamid"])
    print(steam_ID)

    owned_games = api.IPlayerService.GetOwnedGames(steamid=steam_ID, include_appinfo='true', include_played_free_games="false", appids_filter=[], include_free_sub="false")
    print (owned_games['response']["game_count"])
    print("\n")

    guild_ID = ctx.message.guild.id
    author_ID = ctx.message.author.id

    dbHandler.tieIDs(guild_ID, steam_ID, author_ID)

    for i in range(len(owned_games["response"]["games"])):
    #print(i)
    #print(owned_games["response"]["games"][i]["appid"], " ", owned_games["response"]["games"][i]["name"])
        dbHandler.insertGames(steam_ID, guild_ID, owned_games["response"]["games"][i]["appid"], owned_games["response"]["games"][i]["name"])
    
    await ctx.send("Added!")

@bot.command()
async def getgames(ctx):
    guildID = ctx.message.guild.id
    myTitle = "All Games"
    res = dbHandler.getGames(guildID)
    resLength = len(res)
    print(resLength)

    if resLength < 60:
        #strRes = ' '.join(res)
        embedVar = discord.Embed(title=myTitle, description=res, color=0x9CAFBE)
        await ctx.send(embed=embedVar)
    
    else: 
        index = 0
        maxLength = 60

        while index < (resLength - maxLength):
            shortenedRes = res[index:(maxLength+index)]
            embedVar = discord.Embed(title=myTitle, description=shortenedRes, color=0x9CAFBE)
            await ctx.send(embed=embedVar)
            index = index + maxLength
        
        finalRes = res[index-maxLength:]
        embedVar = discord.Embed(title=myTitle, description=finalRes, color=0x9CAFBE)
        await ctx.send(embed=embedVar)


@bot.command()
async def getShared(ctx, member: discord.Member):
    guildID = ctx.message.guild.id
    myTitle = "Shared games between users"
    
    res = dbHandler.getSharedGames(guildID, ctx.message.author.id, member.id)

    resLength = len(res)

    if resLength < 60:
        #strRes = ' '.join(res)
        embedVar = discord.Embed(title=myTitle, description=res, color=0x9CAFBE)
        await ctx.send(embed=embedVar)
    
    else: 
        index = 0
        maxLength = 60

        while index < (resLength - maxLength):
            shortenedRes = res[index:(maxLength+index)]
            embedVar = discord.Embed(title=myTitle, description=shortenedRes, color=0x9CAFBE)
            await ctx.send(embed=embedVar)
            index = index + maxLength
        
        finalRes = res[index-maxLength:]
        embedVar = discord.Embed(title=myTitle, description=finalRes, color=0x9CAFBE)
        await ctx.send(embed=embedVar)





bot.run(DISCORDTOKEN)

# tasks
#move from psycopg to the binary in the requirements.txt
# get .env working with python - Done 4/11
# get docker for the app running - currently added gcc to make the current ver work possibly?