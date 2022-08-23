import psycopg2
from configparser import ConfigParser


def config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser["postgresql"] = {
        "host": "localhost", "database": "BDD_Artistique", "user": "postgres", "password": "r3m1_1995"
    }

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db


'''
conn = psycopg2.connect(
    host="localhost",
    database="BDD_Artistique",
    user="postgres",
    password="r3m1_1995")
'''


def create_tables():
    commands = (
        """
        CREATE TABLE IF NOT EXISTS streamingHistory (
            track_name VARCHAR(255) NOT NULL,
            artist_name VARCHAR(255) NOT NULL,
            endTime TIMESTAMP NOT NULL,
            msPlayed INTEGER NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS tracks (
            track_id VARCHAR(255) NOT NULL PRIMARY KEY,
            track_name VARCHAR(255) NOT NULL,
            track_date VARCHAR(255) NOT NULL,
            track_note INTEGER,
            track_comment VARCHAR(255),
            album_id VARCHAR(255),
            album_name VARCHAR(255),
            artist_id VARCHAR(255) NOT NULL,
            artist_name VARCHAR(255) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS albums (
            album_id VARCHAR(255) NOT NULL PRIMARY KEY,
            album_name VARCHAR(255) NOT NULL,
            album_release VARCHAR(255) NOT NULL,
            album_note INTEGER,
            album_comment VARCHAR(255),
            artist_id VARCHAR(255) NOT NULL,
            artist_name VARCHAR(255) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS artists (
            artist_id VARCHAR(255) NOT NULL PRIMARY KEY,
            artist_name VARCHAR(255) NOT NULL
        )
        """
    )
    conn = None
    try:
        # read the connection parameters
        params = config()
        print(params)
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        print(cur)
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


create_tables()
