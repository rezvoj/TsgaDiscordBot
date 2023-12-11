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
