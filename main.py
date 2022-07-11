from dis import dis
import os
import dbHandler
import discord
from discord.ext import commands

from steam.webapi import WebAPI
from dotenv import load_dotenv

load_dotenv()
STEAMWEBKEY = os.getenv('STEAMWEBKEY')
DISCORDTOKEN = os.getenv('DISCORD_TOKEN')
MYGUILDID = os.getenv('MY_GUILD_ID')
#use .env for this....
api = WebAPI(key= STEAMWEBKEY)

dbHandler.initDB()
print("DB INIT")

#intents = discord.Intents.default()
#intents.message_content = True

#bot = commands.Bot(command_prefix='?', intents=intents)

bot = discord.Bot(debug_guilds=[int(MYGUILDID)])

@bot.slash_command()
async def slashtest(ctx):
    await ctx.respond("Hello")


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.slash_command(description="Input your steam vanity tag to add your games to the bot")
async def add(ctx, vanity: str):
    print (api.ISteamWebAPIUtil.GetServerInfo())
    vanity_dict = api.ISteamUser.ResolveVanityURL(vanityurl=vanity)
    steam_ID = (vanity_dict['response']["steamid"])
    print(steam_ID)

    owned_games = api.IPlayerService.GetOwnedGames(steamid=steam_ID, include_appinfo='true', include_played_free_games="false", appids_filter=[], include_free_sub="false")
    games_added = (owned_games['response']["game_count"])
    print("\n")

    guild_ID = ctx.guild.id
    author_ID = ctx.author.id
    author_Name = ctx.author.name

    print(author_ID)

    dbHandler.tieIDs(guild_ID, steam_ID, author_ID, author_Name)
    await ctx.defer()
    for i in range(len(owned_games["response"]["games"])):
    #print(i)
    #print(owned_games["response"]["games"][i]["appid"], " ", owned_games["response"]["games"][i]["name"])
        dbHandler.insertGames(steam_ID, guild_ID, owned_games["response"]["games"][i]["appid"], owned_games["response"]["games"][i]["name"])
    
    embedVar = discord.Embed(title="Added!", description=games_added, color=0x9CAFBE)
    await ctx.followup.send(embed=embedVar)  

@bot.slash_command(description="Gets all games owned by members of this server")
async def getgames(ctx):
    guildID = ctx.guild.id
    myTitle = "All Games "
    page = 1
    res = dbHandler.getGames(guildID)
    resLength = len(res)
    print(resLength)

    if resLength < 60:
        #strRes = ' '.join(res)
        embedVar = discord.Embed(title=myTitle, description=res, color=0x9CAFBE)
        await ctx.respond(embed=embedVar)
    
    else: 
        index = 0
        maxLength = 60

        while index < (resLength - maxLength):
            shortenedRes = res[index:(maxLength+index)]
            pagedTitle = myTitle + str(page)
            page = page + 1
            embedVar = discord.Embed(title=pagedTitle, description=shortenedRes, color=0x9CAFBE)
            await ctx.respond(embed=embedVar)
            index = index + maxLength
        
        finalRes = res[index:]
        pagedTitle = myTitle + str(page)
        embedVar = discord.Embed(title=pagedTitle, description=finalRes, color=0x9CAFBE)
        await ctx.respond(embed=embedVar)


@bot.slash_command(description="See what games you have in common with up to 3 people on the server")
async def shared(ctx, member: discord.Member, member2: discord.Member = None):
    guildID = ctx.guild.id
    myTitle = "Shared games between users "
    
    if member2 is None:
        res = dbHandler.getSharedGames(guildID, ctx.author.id, member.id)
    
    else: 
        print("3 found")
        res = dbHandler.get3SharedGames(guildID, ctx.author.id, member.id, member2.id)

    resLength = len(res)
    print(resLength)

    if resLength < 60:
        #strRes = ' '.join(res)
        embedVar = discord.Embed(title=myTitle, description=res, color=0x9CAFBE)
        await ctx.respond(embed=embedVar)
    
    else: 
        index = 0
        maxLength = 60

        while index < (resLength - maxLength):
            shortenedRes = res[index:(maxLength+index)]
            embedVar = discord.Embed(title=myTitle, description=shortenedRes, color=0x9CAFBE)
            await ctx.respond(embed=embedVar)
            index = index + maxLength
        
        finalRes = res[index:]
        embedVar = discord.Embed(title=myTitle, description=finalRes, color=0x9CAFBE)
        await ctx.respond(embed=embedVar)

@bot.slash_command(description="See who all owns a specific game on the server")
async def owned(ctx, game: str):
    guildID = ctx.guild.id

    res = dbHandler.getGameOwners(guildID, game)
    embedVar = discord.Embed(title=f"Users who own {game}", description=res)

    await ctx.respond(embed=embedVar)





bot.run(DISCORDTOKEN)

# tasks
#move from psycopg to the binary in the requirements.txt
# get .env working with python - Done 4/11
# get docker for the app running - currently added gcc to make the current ver work possibly? - Done 4/18
# work on speeding up the add function, possibly hand over the games list into the db function and see if not reopening the connection speeds things up?