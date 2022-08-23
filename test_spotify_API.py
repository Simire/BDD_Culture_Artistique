import spotipy
import spotipy.util as util

username = 'yu1t1evnysymt6hvw9r3imz65'
client_id ='3c006958654f417493e7e12b778e8939'
client_secret = 'eb5f0c2a288849149c9f2ad4c42c67e6'
redirect_uri = 'http://localhost:7777/callback'
scope = 'user-read-recently-played'

path = r"C:\Users\Rémi\Documents\Scripts\BDD Culture artistique\MyData\\"

token = util.prompt_for_user_token(username=username, 
                                   scope=scope, 
                                   client_id=client_id,   
                                   client_secret=client_secret,     
                                   redirect_uri=redirect_uri)

print(token)



import ast
import pandas as pd
from typing import List
from os import listdir

def get_streamings(path = path) -> List[dict]:
    
    files = [path + file for file in listdir(path)
             if file.split('.')[0].split("\\")[-1] == 'StreamingHistory']
    print(files)
    
    all_streamings = []
    
    for file in files: 
        with open(file, 'r', encoding='UTF-8') as f:
            new_streamings = ast.literal_eval(f.read())
            all_streamings += [streaming for streaming 
                               in new_streamings]
    return all_streamings

import requests

def get_id(track_name: str, token: str) -> str:
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f'Bearer ' + token,
    }
    params = [
    ('q', track_name),
    ('type', 'track'),
    ]
    try:
        response = requests.get('https://api.spotify.com/v1/search', 
                    headers = headers, params = params, timeout = 5)
        json = response.json()
        first_result = json['tracks']['items'][0]
        track_id = first_result['id']
        return track_id
    except:
        return None
    
def get_features(track_id: str, token: str) -> dict:
    sp = spotipy.Spotify(auth=token)
    try:
        features = sp.audio_features([track_id])
        return features[0]
    except:
        return None
    
    
streamings = get_streamings()
unique_tracks = list(set([streaming['trackName'] for streaming in streamings]))
print(len(unique_tracks))
ranking_tracks = pd.Series([streaming['trackName'] for streaming in streamings]).value_counts()

all_features = {}
for track in unique_tracks[:10]:
    track_id = get_id(track, token)
    features = get_features(track_id, token)
    if features:
        all_features[track] = features

print(all_features)
        
with_features = []
for track_name, features in all_features.items():
    with_features.append({'name': track_name, **features})
    
