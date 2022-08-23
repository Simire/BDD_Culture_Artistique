import psycopg2

from DataBaseFilling.Config import config


def delete_duplicate(table):
    table_cleaned = table + "Cleaned"
    sql = """SELECT DISTINCT *

INTO """ + table_cleaned + """
FROM """ + table + """;

DROP TABLE """ + table + """;

ALTER TABLE """ + table_cleaned + """
RENAME TO """ + table + """; 
        """

    conn = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql)
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

