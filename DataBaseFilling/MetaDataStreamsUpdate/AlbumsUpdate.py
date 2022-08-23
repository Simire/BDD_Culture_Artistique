import requests
import time
from tqdm import tqdm
import psycopg2

from DataBaseFilling.Config import config
from GetDistinctColumns import get_distinct_values_column
from GetTokenSpotify import getTokenSpotify
from GetDataTable import get_data_table
from DeleteDuplicateTable import delete_duplicate


headers = getTokenSpotify()

def get_albums_ids_from_artist_id(artist_id):

    request_url = "https://api.spotify.com/v1/artists/" + artist_id + "/albums"
    # print(request_url)

    try:
        r = requests.get(request_url, headers=headers)

        if r.status_code == 429:
            print(r.headers["Retry-After"])
            time.sleep(int(r.headers["Retry-After"]) + 1)
            print("We waited " + str(int(r.headers["Retry-After"]) + 1) + "s")
            r = requests.get(request_url, headers=headers)

        # print(r.json()["items"][0])
        albums_ids = [album_item["id"] for album_item in r.json()["items"]]

    except IndexError:
        albums_ids = []
        print(request_url)
        r = requests.get(request_url, headers=headers)
        print(artist_id + " : IndexError")
        print(r)
        print(r.json())

    except:
        print(request_url)
        r_track = requests.get(request_url, headers=headers)
        print(artist_id + " : Exception")
        print(r_track)
        print(r_track.json())
        albums_ids = []

    return albums_ids


def get_album_data_from_album_id(album_ids):

    albums_data = []
    url_request = "https://api.spotify.com/v1/albums?ids=" + ",".join(album_ids)
    # print(url_request)

    try:
        # print(url_tracks + ",".join(tracks_ids))
        r = requests.get(url_request, headers=headers)

        if r.status_code == 429:
            time.sleep(int(r.headers["Retry-After"]) + 1)
            r = requests.get(url_request, headers=headers)

        for album_data in r.json()["albums"]:
            try:
                albums_data.append((album_data["id"],
                                    album_data["name"],
                                    album_data["release_date"],
                                    album_data["artists"][0]["id"],
                                    album_data["artists"][0]["name"]
                                    ))
            except:
                albums_data.append(album_data)

    except IndexError:
        r = requests.get(url_request, headers=headers)
        print(str(album_ids) + " : IndexError")
        print(r)
        # print(r.json()['tracks']["id"])

    except:
        r = requests.get(url_request, headers=headers)
        print(str(album_ids) + " : Exception")
        print(r)
        # print(r.json()['tracks']["id"])

    return albums_data


def extract_albums_data_from_id_by_parts(all_album_ids, parts_size):

    num_parts_list = (len(all_album_ids) - 1) // parts_size
    print(range(num_parts_list))

    if len(all_album_ids) > parts_size:
        album_data = []
        for num_it in tqdm(range(num_parts_list + 1)):
            lower_bound = num_it * parts_size
            upper_bound = min(len(all_album_ids), (num_it + 1) * parts_size)
            album_data = album_data + get_album_data_from_album_id(list(all_album_ids)[lower_bound:upper_bound])
    else:
        album_data = get_album_data_from_album_id(all_album_ids)

    return album_data


def insert_album_data_in_album_table(album_data):

    sql = """INSERT INTO albums(album_id, album_name, album_release,
                            artist_id, artist_name) 
                VALUES(%s,%s,%s,
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
        if type(album_data) == tuple:
            cur.execute(sql, album_data)
        elif type(album_data) == list:
            cur.executemany(sql, album_data)
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

    return


def albums_update():

    artist_ids = get_distinct_values_column(column="artist_id", table="artists")
    print(artist_ids[:10])

    # artist_id looks like : (artist_id,)
    all_album_ids_by_artist = {artist_id[0]: get_albums_ids_from_artist_id(artist_id[0]) for artist_id in tqdm(artist_ids)}  # [:10]
    print({k: all_album_ids_by_artist[k] for k in list(all_album_ids_by_artist)[:10]})

    all_album_ids = [album_id for album_ids_by_artist in list(all_album_ids_by_artist.values())
                     for album_id in album_ids_by_artist]
    print(len(all_album_ids))
    all_album_ids = list(set(all_album_ids))
    print(len(all_album_ids))

    album_data = extract_albums_data_from_id_by_parts(all_album_ids, parts_size=20)
    print(album_data[:10])

    insert_album_data_in_album_table(album_data)
    get_data_table("albums", "album_id")
    delete_duplicate("albums")
    get_data_table("albums", "album_id")

    return
