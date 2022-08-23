import requests
import time
from tqdm import tqdm
from urllib.parse import quote_plus
import psycopg2

from DataBaseFilling.Config import config
from GetDistinctColumns import get_distinct_values_column
from GetTokenSpotify import getTokenSpotify
from GetDataTable import get_data_table
from DeleteDuplicateTable import delete_duplicate


def track_name_correction(track_name):

    track_name = quote_plus(track_name, safe='')  # When separators not allowed URL
    track_name_and = track_name.replace('%', "&%")  # When 2 following separators are replaced
    track_name_space = track_name_and.replace('-+&%', "-+%")  # When there is space + sep -> not needed

    return track_name_space


url_search = "https://api.spotify.com/v1/search?q="
type_track_str = "&type=track"
type_artist_str = "&type=artist"
headers = getTokenSpotify()


def get_track_id(track_name, artist_name):

    str_track = "track:"
    str_artist = "artist:"
    separator = "&%20"

    track_name = track_name.split(" - ")[0] if "emastered" in track_name else track_name

    request_url = url_search + \
                  str_track + \
                  track_name_correction(track_name) + \
                  separator + \
                  str_artist + \
                  artist_name + \
                  type_track_str

    try:
        r_track = requests.get(request_url, headers=headers)
        # print(request_url)
        # print(r_track.json()["tracks"]["items"][0])
        if r_track.status_code == 429:
            print(r_track.headers["Retry-After"])
            time.sleep(int(r_track.headers["Retry-After"]) + 1)
            print("We waited " + str(int(r_track.headers["Retry-After"]) + 1) + "s")
            r_track = requests.get(request_url, headers=headers)
        # print(r)
        # print(r.status_code == 429)
        # print(request_url)
        # print(r_track.json()["tracks"]["items"][0])
        track_id = r_track.json()["tracks"]["items"][0]["id"]
        # print(track_id)
    except IndexError:
        track_id = ''
        print(request_url)
        r_track = requests.get(url_search + track_name + type_track_str, headers=headers)
        print(track_name + " : IndexError")
        print(r_track)
        print(r_track.json())
    except:
        print(request_url)
        r_track = requests.get(url_search + track_name + type_track_str, headers=headers)
        print(track_name + " : Exception")
        print(r_track)
        print(r_track.json())
        track_id = ''

    return track_id


url_tracks = "https://api.spotify.com/v1/tracks?ids="


def get_tracks_data_from_id(tracks_ids):

    tracks_data = []

    try:
        # print(url_tracks + ",".join(tracks_ids))
        r = requests.get(url_tracks + ",".join(tracks_ids), headers=headers)

        if r.status_code == 429:
            time.sleep(int(r.headers["Retry-After"]) + 1)
            r = requests.get(url_tracks + ",".join(tracks_ids), headers=headers)

        for track_data in r.json()['tracks']:
            try :
                tracks_data.append((track_data["id"],
                        track_data["name"],
                        track_data["album"]["release_date"],
                        track_data["album"]["id"],
                        track_data["album"]["name"],
                        track_data["artists"][0]["id"],
                        track_data["artists"][0]["name"]
                        ))
            except :
                tracks_data.append(track_data)

    except IndexError:
        r = requests.get(url_search + ",".join(tracks_ids), headers=headers)
        print(str(tracks_ids) + " : IndexError")
        print(r)
        # print(r.json()['tracks']["id"])

    except:
        r = requests.get(url_search + ",".join(tracks_ids), headers=headers)
        print(str(tracks_ids) + " : Exception")
        print(r)
        # print(r.json()['tracks']["id"])

    return tracks_data


def get_duplicated_ids(dict_track_artist_name_id):
    rev_multidict = {}
    for key, value in dict_track_artist_name_id.items():
        rev_multidict.setdefault(value, set()).add(key)

    ids = [key for key, values in rev_multidict.items() if len(values) > 1]
    return ids


def insert_track(track):
    sql = """INSERT INTO tracks(track_id, track_name, track_date,
                        album_id, album_name,
                        artist_id, artist_name) 
            VALUES(%s,%s,%s,
            %s,%s,
            %s,%s)"""

    conn = None
    track_name = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        if type(track) == tuple:
            cur.execute(sql, track)
        elif type(track) == list:
            cur.executemany(sql, track)
        else:
            print("Entry type is neither of list (multiple tracks) nor tuple (single track)")
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return track_name


def extract_tracks_data_from_id_by_parts(tracks_ids, parts_size):

    num_parts_list = (len(tracks_ids) - 1) // parts_size
    print(range(num_parts_list))

    if len(tracks_ids) > parts_size:
        tracks_data = []
        for num_it in tqdm(range(num_parts_list + 1)):
            lower_bound = num_it * parts_size
            upper_bound = min(len(tracks_ids), (num_it + 1) * parts_size)
            tracks_data = tracks_data + get_tracks_data_from_id(list(tracks_ids.values())[lower_bound:upper_bound])
    else:
        tracks_data = get_tracks_data_from_id(tracks_ids)

    return tracks_data


def tracks_update():

    tracks_names = get_distinct_values_column(column="track_name, artist_name", table="streamingHistory")
    print(len(tracks_names))
    print(tracks_names[:10])

    print(get_track_id(tracks_names[0][0], tracks_names[0][1]))
    tracks_ids = {(track_artist_name[0], track_artist_name[1]): get_track_id(track_artist_name[0], track_artist_name[1])
                  for track_artist_name in tqdm(tracks_names)}  # [:100]
    print({k: tracks_ids[k] for k in list(tracks_ids)[:10]})
    print(len(tracks_ids))
    tracks_ids = {key: value for key, value in tracks_ids.items() if value != ""}
    print(len(tracks_ids))

    ids_duplicated = get_duplicated_ids(tracks_ids)
    print(ids_duplicated)
    print(len(ids_duplicated))

    tracks_data = extract_tracks_data_from_id_by_parts(tracks_ids, parts_size=50)
    print(tracks_data[:10])
    print(len(tracks_data))

    insert_track(tracks_data)
    get_data_table("tracks", "track_id")
    delete_duplicate("tracks")
    get_data_table("tracks", "track_id")

    return
