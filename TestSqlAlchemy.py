import pandas as pd
from sqlalchemy import Column, Integer, Text, MetaData, Table
import json

# Loading data

path = r"C:\Users\Rémi\Documents\Scripts\BDD Culture artistique\MyData"
json_name = r"\StreamingHistory.json"
with open(path + json_name, 'r', encoding="utf8") as f:
  streamingHistory = json.load(f)

print(streamingHistory[0])
print(len(streamingHistory))

# Creating SQL DB

from sqlalchemy import create_engine

engine = create_engine('sqlite://')

metadata = MetaData()
messages = Table(
    'messages', metadata,
    Column('id', Integer, primary_key=True),
    Column('message', Text),
)

messages.create(bind=engine)

'''
#### Dans d'autres files quand on a géré la DB

# Connect spotify API

import requests
import base64
# import json
# from secrets import *

# Step 1 - Authorization
clientId = "3c006958654f417493e7e12b778e8939"
clientSecret = "eb5f0c2a288849149c9f2ad4c42c67e6"
#SPOTIPY_REDIRECT_URI = "http://localhost:7777/callback"

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
    'redirect_uri': 'https://open.spotify.com/collection/playlists',
    #'client_id': CLIENT_ID,
    #'client_secret': CLIENT_SECRET,
}

# Encode as Base64

message = f"{clientId}:{clientSecret}"
messageBytes = message.encode('ascii')
base64Bytes = base64.b64encode(messageBytes)
base64Message = base64Bytes.decode('ascii')

print(message)
print(messageBytes)
print(base64Bytes)
print(base64Message)
print()

headers['Authorization'] = f"Basic {base64Message}"
data['grant_type'] = "client_credentials"


r = requests.post(url, headers=headers, data=data)

token = r.json()['access_token']
print(token)

url_search = "https://api.spotify.com/v1/search?q=You%20Ain't%20The%20Problem&type=track"
headers = {"Authorization": "Bearer " + token}
r = requests.get(url_search, headers=headers)

data = r.json()
print(data["tracks"]["items"][0]["id"])
print(data["tracks"]["items"][0]["album"]["name"])

url_tracks = "https://api.spotify.com/v1/tracks/3zJ5RDG0bLQAV2rntFgUtb"
headers = {"Authorization": "Bearer " + token}
r = requests.get(url_tracks, headers=headers)

data = r.json()
print(data["name"])

'''
# Connect spotify API with spotipy

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

SPOTIPY_CLIENT_ID = "3c006958654f417493e7e12b778e8939"
SPOTIPY_CLIENT_SECRET = "eb5f0c2a288849149c9f2ad4c42c67e6"
SPOTIPY_REDIRECT_URI = "http://localhost:7777/callback"

sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = SPOTIPY_CLIENT_ID,
                                       client_secret = SPOTIPY_CLIENT_SECRET,
                                       redirect_uri = SPOTIPY_REDIRECT_URI,
                                       #scope=SCOPE,
                                       #cache_path=CACHE,
                                       show_dialog=True
                                       )

sp = spotipy.Spotify(sp_oauth)
#auth_manager = SpotifyClientCredentials()
#sp = spotipy.Spotify(auth_manager=auth_manager)

#sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())
#result = sp.search(q = "track:De quoi te plaire", type = "track")
#print(result)

#spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(), )

# Visualize dataframe

desired_width = 320
pd.set_option('display.width', desired_width)
pd.set_option('display.max_columns', 10)

streamingHistoryDF = pd.DataFrame(streamingHistory)
print(streamingHistoryDF.head())
print(streamingHistoryDF["trackName"].value_counts()[:10])

# DF modification

url_search = "https://api.spotify.com/v1/search?q="
type_str = "&type=track"
# You%20Ain't%20The%20Problem&type=track"
headers = {"Authorization": "Bearer " + token}


def extract_album_name(track_name, url_search, type_str, headers):

    try:
        r = requests.get(url_search + track_name + type_str, headers=headers)
        album_name = r.json()["tracks"]["items"][0]["album"]["name"]
    except IndexError:
        album_name = ''
        r = requests.get(url_search + track_name + type_str, headers=headers)
        print(track_name + " : IndexError")
        print(r)
        print(r.json()["tracks"])
    except :
        r = requests.get(url_search + track_name + type_str, headers=headers)
        print(track_name + " : Exception")
        print(r)
        album_name = ''

    return album_name


print(streamingHistoryDF.shape)
streamingHistoryDF["album"] = streamingHistoryDF["trackName"].apply(lambda x : extract_album_name(x,
                                                                                                  url_search,
                                                                                                  type_str,
                                                                                                  headers))

print(streamingHistoryDF["album"][:10])

# Ranking

ranking_tracks = streamingHistoryDF.groupby(["trackName", "artistName"]).count().reset_index()
print(ranking_tracks["endTime"].max())
print(ranking_tracks.sort_values("endTime", ascending = False).head(15))

ranking_albums = streamingHistoryDF.groupby(["albumName"]).count().reset_index()
print(ranking_albums["endTime"].max())
print(ranking_albums.sort_values("endTime", ascending = False).head(15))


