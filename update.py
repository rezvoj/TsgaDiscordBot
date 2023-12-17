import discord, database, sqlite3, datetime, twitch_api, asyncio, time

updateDelay = 30



def sendToUser(dcClient: discord.Client, userId, message):
    try:
        coorutine = dcClient.fetch_user(userId)
        user = asyncio.run_coroutine_threadsafe(coorutine, dcClient.loop).result()
        asyncio.run_coroutine_threadsafe(user.send(message), dcClient.loop)
    except Exception as ex:
        print(f"An error occurred sending message to user {userId}: {ex}")


def update(dcClient: discord.Client, dbConnection: sqlite3.Connection):
    for streamerId, status in database.getStreamers(dbConnection):
        streamInfo = twitch_api.getStreamInfo(twitch_api.clientId, twitch_api.accessToken, streamerId)
        if streamInfo is None:
            if status != -1:
                database.updateStreamerStatus(dbConnection, streamerId, -1)
        elif status != str(streamInfo['game_id']):
            database.updateStreamerStatus(dbConnection, streamerId, streamInfo['game_id'])
            message = f"[{streamInfo['user_login']}](<https://www.twitch.tv/{streamInfo['user_login']}>)"
            message += f" is now streaming {streamInfo['game_name']}: {streamInfo['title']}"            
            for userId in database.getUsersForStreamerStatus(dbConnection, streamerId, streamInfo['game_id']):
                sendToUser(dcClient, userId, message)
    now = datetime.datetime.now()
    if twitch_api.accessTokenDtm + datetime.timedelta(days=1) < now:
        twitch_api.accessToken = twitch_api.getAccessToken(twitch_api.clientId, twitch_api.clientSecret)
        twitch_api.accessTokenDtm = now
    print(f"Update Completed - {datetime.datetime.now()}")
    return "OK"


def run(dcClient: discord.Client):
    print(f"Update Loop Starting {datetime.datetime.now()}")
    with database.getConnection("data.db") as dbConnection:
        while True:
            update(dcClient, dbConnection)
            time.sleep(updateDelay)
