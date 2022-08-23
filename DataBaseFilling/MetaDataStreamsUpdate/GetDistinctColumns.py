import psycopg2
from DataBaseFilling.Config import config


def get_distinct_values_column(column, table):  # Test if column in table not list of columns

    conn = None

    if column in ["track_name", "artist_name", "track_name, artist_name", "artist_id"]:
        pass
    else:
        print("Please choose a column in this list : [track_name, artist_name, track_name, artist_name, artist_id]")
        return

    distinct_elements_column = []

    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT " + column + " FROM " + table)
        print("The number of parts: ", cur.rowcount)
        distinct_elements_column = cur.fetchall()
        row = cur.fetchone()

        while row is not None:
            # print(row)
            row = cur.fetchone()

        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    return distinct_elements_column
