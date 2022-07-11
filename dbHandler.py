import os
from dotenv import load_dotenv


load_dotenv()
DB_PASSWORD = os.getenv('POSTPASS')

import psycopg

def initDB():
    with psycopg.connect("dbname=postgres host=localhost user=postgres", password=DB_PASSWORD)as conn:
    # Open a cursor to perform database operations
        with conn.cursor() as cur:

        # Execute a command: this creates a new table
            cur.execute("""CREATE TABLE IF NOT EXISTS games (steamid BIGINT, guildid BIGINT, appid INTEGER, appname TEXT, PRIMARY KEY (steamid, guildid, appid))""")

            cur.execute("CREATE TABLE IF NOT EXISTS users (guildid BIGINT, steamid BIGINT, discordid BIGINT, discordname TEXT, PRIMARY KEY (guildid, steamid))")
            conn.commit()

def tieIDs(guildID, steamID, authorID, authorName):
    with psycopg.connect("dbname=postgres host=localhost user=postgres", password=DB_PASSWORD)as conn:
        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            cur.execute("INSERT INTO users (guildid, steamid, discordid, discordname) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", (guildID, steamID, authorID, authorName))
            print("ID's Tied")

def insertGames(steamID, guildID, appID, appName):
    with psycopg.connect("dbname=postgres host=localhost user=postgres", password=DB_PASSWORD)as conn:
        # Open a cursor to perform database operations
        with conn.cursor() as cur:

            
            # Pass data to fill a query placeholders and let Psycopg perform
            # the correct conversion (no SQL injections!)
            cur.execute(
                "INSERT INTO games (steamid, guildid, appid, appname) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
                (steamID, guildID, appID, appName))
            return(steamID)

        
#keep this as a way to check all server owned games? tie to guildID
def getGames(guildID):
    with psycopg.connect("dbname=postgres host=localhost user=postgres", password=DB_PASSWORD)as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT appname FROM games WHERE guildid = (%s)", (guildID,))
            res = cur.fetchall()
            res =[i[0] for i in res]
            #print(res)

            #reducedRes = res[0:49]
            return(res)

#get some form of formatting on this
def getSharedGames(guildID, authorID, mentionedID):
    with psycopg.connect("dbname=postgres host=localhost user=postgres", password=DB_PASSWORD)as conn:
        with conn.cursor() as cur:

            row = cur.execute("SELECT steamid FROM users WHERE guildid = (%s) AND discordid = (%s)", (guildID, authorID)).fetchone()
            authorSteamID = row[0]
            row = cur.execute("SELECT steamid FROM users WHERE guildid = (%s) AND discordid = (%s)", (guildID, mentionedID)).fetchone()
            mentionedSteamID = row[0]
            print(authorSteamID)
           
            cur.execute("SELECT DISTINCT g1.appname FROM games g1 INNER JOIN games g2 ON g1.appid = g2.appid WHERE g1.steamid = (%s) AND g2.steamid = (%s) AND g1.steamid !=g2.steamid AND g1.guildid = (%s) AND g2.guildid = (%s)",
            (authorSteamID, mentionedSteamID, guildID, guildID))
            res = cur.fetchall()
            res = [i[0] for i in res]

            return(res)

            #for record in cur:
                #return(record)

def get3SharedGames(guildID, authorID, mentionedID, mentioned2ID):
    with psycopg.connect("dbname=postgres host=localhost user=postgres", password=DB_PASSWORD)as conn:
        with conn.cursor() as cur:

            row = cur.execute("SELECT steamid FROM users WHERE guildid = (%s) AND discordid = (%s)", (guildID, authorID)).fetchone()
            authorSteamID = row[0]

            row = cur.execute("SELECT steamid FROM users WHERE guildid = (%s) AND discordid = (%s)", (guildID, mentionedID)).fetchone()
            mentionedSteamID = row[0]

            row = cur.execute("SELECT steamid FROM users WHERE guildid = (%s) AND discordid = (%s)", (guildID, mentioned2ID)).fetchone()
            mentioned2SteamID = row[0]

            print(authorSteamID, " ", mentionedSteamID, " ", mentioned2SteamID)
            
           
            cur.execute("SELECT DISTINCT g1.appname FROM games g1 INNER JOIN games g2 ON g1.appid = g2.appid INNER JOIN games g3 ON g2.appid = g3.appid WHERE g1.steamid = (%s) AND g2.steamid = (%s) AND g3.steamid = (%s) AND g1.steamid != g2.steamid AND g2.steamid != g3.steamid AND g1.guildid = (%s) AND g2.guildid = (%s) AND g3.guildid = (%s)",
            (authorSteamID, mentionedSteamID, mentioned2SteamID, guildID, guildID, guildID))
            res = cur.fetchall()
            res = [i[0] for i in res]
            return(res)

def getGameOwners(guildID, game):
    with psycopg.connect("dbname=postgres host=localhost user=postgres", password=DB_PASSWORD)as conn:
        with conn.cursor() as cur:

            cur.execute("SELECT steamid FROM games WHERE appname = (%s) AND guildid = (%s)", (game, guildID))
            ownedSteamID = cur.fetchall()
            ownedSteamID = [i[0] for i in ownedSteamID]
    

            cur.execute("SELECT discordname FROM users WHERE steamid = ANY(%s)", (ownedSteamID,))

            gameOwners = cur.fetchall()
            res = [i[0] for i in gameOwners]
            print(type(res))

            return(res)