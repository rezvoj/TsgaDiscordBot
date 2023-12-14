import discord, datetime, database, asyncio, tokens

intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
client = discord.Client(intents=intents)
dbConnection = database.getConnection("data.db")



@client.event
async def on_ready():
    print(f"Bot Ready {datetime.datetime.now()}")


async def sendContentList(message: discord.Message, contentList: dict):
    if not len(contentList):
        return await message.reply("Nothing to show.")
    embed = discord.Embed(color=discord.Color.blue())
    for name, items in contentList.items():
        gamesList = "\n".join(items)
        embed.add_field(name=name, value=gamesList or "\u200b", inline=False)
    return await message.reply(embed=embed)


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


def run():
    database.initDB(dbConnection)
    client.run(tokens.DISCORD_TOKEN)
    dbConnection.close()
