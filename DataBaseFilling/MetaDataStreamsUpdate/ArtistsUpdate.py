from tqdm import tqdm
import requests
import time
import psycopg2

from GetDistinctColumns import get_distinct_values_column
from GetTokenSpotify import getTokenSpotify
from DataBaseFilling.Config import config
from GetDataTable import get_data_table
from DeleteDuplicateTable import delete_duplicate


url_search = "https://api.spotify.com/v1/search?q="
type_track_str = "&type=track"
type_artist_str = "&type=artist"
headers = getTokenSpotify()


def get_artist_id(artist_name):

    try:
        r = requests.get(url_search + artist_name + type_artist_str, headers=headers)
        if r.status_code == 429:
            print(r.headers["Retry-After"])
            time.sleep(int(r.headers["Retry-After"]) + 1)
            print("We waited " + str(int(r.headers["Retry-After"]) + 1) + "s")
            r = requests.get(url_search + artist_name + type_artist_str, headers=headers)
        artist_id = r.json()["artists"]["items"][0]["id"]
    except IndexError:
        artist_id = ''
        r = requests.get(url_search + artist_name + type_artist_str, headers=headers)
        print(artist_name + " : IndexError")
        print(r)
        print(r.json()["artists"])
    except:
        r = requests.get(url_search + artist_name + type_artist_str, headers=headers)
        print(artist_name + " : Exception")
        print(r)
        artist_id = ''

    return artist_id


def insert_artist(artist):
    sql = """
    INSERT INTO artists(artist_name,artist_id) 
    VALUES(%s,%s);
    """

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
        if type(artist) == tuple:
            cur.execute(sql, artist)
        elif type(artist) == list:
            cur.executemany(sql, artist)
        else:
            print("Entry type is neither of list (multiple artists) nor tuple (single artist)")
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


def artists_update():
    artists_names = get_distinct_values_column(column="artist_name", table="streamingHistory")

    print(len(artists_names))
    print(artists_names[:10])

    # artist_data looks like : (artist_name,)
    artists_data = [(artist_data[0], get_artist_id(artist_data[0])) for artist_data in tqdm(artists_names)]
    print(artists_data[:3])

    print(len(artists_data))
    print(type(artists_data))

    insert_artist(artists_data)
    delete_duplicate("artists")
    get_data_table("artists", "artist_name")

    return
