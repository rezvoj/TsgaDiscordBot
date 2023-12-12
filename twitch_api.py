import requests, tokens, datetime, threading

def getAccessToken(clientId, clientSecret):
    url = 'https://id.twitch.tv/oauth2/token'
    payload = {
        'client_id': clientId, 
        'client_secret': clientSecret, 
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        return response.json()['access_token']
    raise Exception(f"Error: {response.status_code} - {response.text}")


clientId = tokens.TWITCH_ID
clientSecret = tokens.TWITCH_SECRET
accessToken = getAccessToken(clientId, clientSecret)
accessTokenDtm = datetime.datetime.now()



def getStreamInfo(clientId, accessToken, userId):
    streams_url = 'https://api.twitch.tv/helix/streams'
    headers = {
        'Client-ID': clientId,
        'Authorization': f'Bearer {accessToken}'
    }
    params = {'user_id': userId}
    response = requests.get(streams_url, headers=headers, params=params)
    if response.status_code == 200:
        streamData = response.json()['data']
        if streamData:
            return streamData[0]
        return None
    raise Exception(f"Error: {response.status_code} - {response.text}")


def getGameId(clientId, accessToken, gameName):
    url = 'https://api.twitch.tv/helix/games'
    headers = {
        'Client-ID': clientId,
        'Authorization': f'Bearer {accessToken}'
    }
    params = {'name': gameName}    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        gameData = response.json()['data']
        if gameData:
            return gameData[0]['id']
        return None
    raise Exception(f"Error: {response.status_code} - {response.text}")


def getGameName(clientId, accessToken, gameId):
    url = 'https://api.twitch.tv/helix/games'
    headers = {
        'Client-ID': clientId,
        'Authorization': f'Bearer {accessToken}'
    }
    params = {'id': gameId}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        gameData = response.json()['data']
        if gameData:
            return gameData[0]['name']
        return None
    raise Exception(f"Error: {response.status_code} - {response.text}")


def getStreamerId(clientId, accessToken, streamerLogin):
    url = 'https://api.twitch.tv/helix/users'
    headers = {
        'Client-ID': clientId,
        'Authorization': f'Bearer {accessToken}'
    }
    params = {'login': streamerLogin}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        userData = response.json()['data']
        if userData:
            return userData[0]['id']
        return None
    raise Exception(f"Error: {response.status_code} - {response.text}")


def getStreamerName(clientId, accessToken, streamerId):
    url = 'https://api.twitch.tv/helix/users'
    headers = {
        'Client-ID': clientId,
        'Authorization': f'Bearer {accessToken}'
    }
    params = {'id': streamerId}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        userData = response.json()['data']
        if userData:
            return userData[0]['login']
        return None
    raise Exception(f"Error: {response.status_code} - {response.text}")
