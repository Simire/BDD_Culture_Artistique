import base64
import requests

# Requests spotify


def getTokenSpotify():

    clientId = "3c006958654f417493e7e12b778e8939"
    clientSecret = "eb5f0c2a288849149c9f2ad4c42c67e6"
    # SPOTIPY_REDIRECT_URI = "http://localhost:7777/callback"

    message = f"{clientId}:{clientSecret}"
    messageBytes = message.encode('ascii')
    base64Bytes = base64.b64encode(messageBytes)
    base64Message = base64Bytes.decode('ascii')

    auth_url = 'https://accounts.spotify.com/authorize'
    url = "https://accounts.spotify.com/api/token"
    auth_header = base64.urlsafe_b64encode((clientId + ':' + clientSecret).encode('ascii'))
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic %s' % auth_header.decode('ascii')
    }

    auth_code = requests.get(auth_url, {
        'client_id': clientId,
        'response_type': 'code',
        'redirect_uri': 'https://open.spotify.com/collection/playlists',
        'scope': 'playlist-modify-private',
    })

    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': 'https://open.spotify.com/collection/playlists'
        #'client_id': CLIENT_ID,
        #'client_secret': CLIENT_SECRET,
    }

    headers['Authorization'] = f"Basic {base64Message}"
    data['grant_type'] = "client_credentials"

    r_token = requests.post(url, headers=headers, data=data)
    print(r_token.json())

    token = r_token.json()['access_token']
    headers = {"Authorization": "Bearer " + token}

    return headers
