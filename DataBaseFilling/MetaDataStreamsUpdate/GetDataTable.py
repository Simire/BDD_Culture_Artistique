import psycopg2

from DataBaseFilling.Config import config


def get_data_table(table, column_order):

    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT * FROM " + table + " ORDER BY " + column_order)
        print("The number of parts: ", cur.rowcount)
        row = cur.fetchone()

        while row is not None:
            #print(row)
            row = cur.fetchone()

        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return
