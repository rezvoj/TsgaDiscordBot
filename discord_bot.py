import discord, datetime, database, twitch_api, asyncio, tokens

intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
client = discord.Client(intents=intents)
dbConnection = database.getConnection("data.db")



@client.event
async def on_ready():
    print(f"Bot Ready {datetime.datetime.now()}")


async def getStreamerId(message: discord.Message, streamerName: str):
    streamerId = twitch_api.getStreamerId(twitch_api.clientId, twitch_api.accessToken, streamerName)
    if streamerId is None:
        await asyncio.gather(
            message.reply(f'Streamer "{streamerName}" does not exist.'),
            message.add_reaction('❌')
        )
        return None
    return str(streamerId)


async def getStreamerGameId(message: discord.Message, usageString: str):
    try:
        noprefix = message.content.strip().removeprefix(usageString).strip()
        streamerName, gameName = map(str.strip, noprefix.split(" ", maxsplit=1))
    except ValueError:
        await asyncio.gather(
            message.reply(f'Usage: {usageString} <streamer> <game>.'),
            message.add_reaction('❌')
        )
        return None, None
    streamerId = await getStreamerId(message, streamerName)
    if streamerId is None:
        return None, None
    gameId = twitch_api.getGameId(twitch_api.clientId, twitch_api.accessToken, gameName)
    if gameId is None:
        await asyncio.gather(
            message.reply(f'Game "{gameName}" does not exist.'),
            message.add_reaction('❌')
        )
        return None, None
    return str(streamerId), str(gameId)


async def watch(message: discord.Message):
    streamerId, gameId = await getStreamerGameId(message, "!tsga watch")
    if streamerId is None:
        return
    database.addStreamerUserStatus(dbConnection, message.author.id, streamerId, gameId)
    if database.getStreamerStatus(dbConnection, streamerId) == gameId:
        streamInfo = twitch_api.getStreamInfo(twitch_api.clientId, twitch_api.accessToken, streamerId)
        if streamInfo is not None and str(streamInfo['game_id']) == gameId:
            reply = f"[{streamInfo['user_login']}](<https://www.twitch.tv/{streamInfo['user_login']}>)"
            reply += f" is now streaming {streamInfo['game_name']}: {streamInfo['title']}"
            await message.reply(reply)
    await message.add_reaction('✅')


async def unwatch(message: discord.Message):
    streamerName = message.content.strip().removeprefix("!tsga unwatch").strip()
    if streamerName == "":
        database.removeForUser(dbConnection, message.author.id)
    elif " " in streamerName:
        streamerId, gameId = await getStreamerGameId(message, "!tsga unwatch")
        if streamerId is None:
            return
        database.removeForUser(dbConnection, message.author.id, streamerId, gameId)
    else:
        streamerId = await getStreamerId(message, streamerName)
        if streamerId is None:
            return
        database.removeForUser(dbConnection, message.author.id, streamerId)
    await message.add_reaction('✅')


async def sendContentList(message: discord.Message, contentList: dict):
    if not len(contentList):
        return await message.reply("Nothing to show.")
    embed = discord.Embed(color=discord.Color.blue())
    for name, items in contentList.items():
        gamesList = "\n".join(items)
        embed.add_field(name=name, value=gamesList or "\u200b", inline=False)
    return await message.reply(embed=embed)


def appendStreamerGames(streamersList: dict, gameNameCache: dict, streamerName: str, gameIds: list):
    streamersList[streamerName] = list()
    for gameId in gameIds:
        if gameId not in gameNameCache:
            gameNameCache[gameId] = twitch_api.getGameName(twitch_api.clientId, twitch_api.accessToken, gameId)
        if gameNameCache[gameId] is not None:
            streamersList[streamerName].append(gameNameCache[gameId])
    if len(streamersList[streamerName]) == 0:
        streamersList.pop(streamerName)


async def watchedList(message: discord.Message):
    streamerName = message.content.strip().removeprefix("!tsga list").strip()
    streamerId = None if streamerName == "" else await getStreamerId(message, streamerName)
    streamersList, gameNameCache = dict(), dict()
    for streamerId, gameIds in database.listForUser(dbConnection, message.author.id, streamerId).items():
        streamerName = twitch_api.getStreamerName(twitch_api.clientId, twitch_api.accessToken, streamerId)
        if streamerName is not None:
            appendStreamerGames(streamersList, gameNameCache, streamerName, gameIds)
    await asyncio.gather(
        sendContentList(message, streamersList),
        message.add_reaction('✅')
    )


async def help(message: discord.Message):
    helpList = {
        "!tsga list": ["Show list of streamers and watched games."],
        "!tsga list <streamer>": ["Show list of watched games for specified streamer."],
        "!tsga watch <streamer> <game>": ["Register game to watch for when specified streamer streames it."],
        "!tsga unwatch <streamer> <game>": ["Unregister watched for game for specified streamer."],
        "!tsga unwatch <streamer>": ["Unregister all watched for games for specified streamer."],
        "!tsga unwatch": ["Unregister all watched for games of all streamers."],
        "!tsga help": ["Show this lists."],
    }
    await asyncio.gather(
        sendContentList(message, helpList),
        message.add_reaction('✅')
    )


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    if message.content.lstrip().startswith("!tsga help"):
        await help(message)
    if message.content.lstrip().startswith("!tsga watch"):
        await watch(message)
    elif message.content.lstrip().startswith("!tsga unwatch"):
        await unwatch(message)
    elif message.content.lstrip().startswith("!tsga list"):
        await watchedList(message)


def run():
    database.initDB(dbConnection)
    client.run(tokens.DISCORD_TOKEN)
    dbConnection.close()
