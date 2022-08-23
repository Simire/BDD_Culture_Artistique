import json
import psycopg2
from Config import config

# Loading data

path = r"/Data/MyData_08_22"
json_name = r"\StreamingHistory.json"
with open(path + json_name, 'r', encoding="utf8") as f:
  streamingHistory = json.load(f)

print(streamingHistory[0])
print(len(streamingHistory))


# Insert track


def insert_track(track):
    sql = """INSERT INTO streamingHistory(track_name,artist_name,endTime,msPlayed) VALUES(%s,%s,%s,%s)"""

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


# Delete_duplicates


def delete_duplicate():
    sql = """SELECT DISTINCT *

INTO streamingHistoryCleaned
FROM streamingHistory;

DROP TABLE streamingHistory;

ALTER TABLE streamingHistoryCleaned
RENAME TO streamingHistory; 
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




def get_tracks():
    """ query data from the vendors table """
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT track_name,artist_name,endTime,msPlayed FROM streamingHistory ORDER BY endTime")
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


if __name__ == "__main__":
    tracks = streamingHistory
    tuple_tracks = [(track["trackName"], track["artistName"], track["endTime"], track["msPlayed"]) for track in tracks]
    print(len(tuple_tracks))
    print(type(tuple_tracks))

    insert_track(tuple_tracks)
    delete_duplicate()
    get_tracks()


'''

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import *


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'main.db')

db = SQLAlchemy(app)


data = {
   "all_orders": [
      {
         "id": 456213548,
         "created_at": "2018-11-04T23:18:18-02:00",
         "number": null
      },
      {
         "id":4562222222,
         "created_at": "2018-11-04T23:18:18-02:00",
         "number": 1982,
      }
   ]
}


class SalesOrders(db.Model):
    __tablename__ = 'sales_orders'

    order_id = db.Column(db.String(50), primary_key=True, server_default='')
    order_number = db.Column(db.String(50))
    created_at = db.Column(db.String(50))


def update_orders(data):
    orders_entries = []
    for orders in data["all_orders"]:
        new_entry = SalesOrders(order_id=orders['id'],
                                order_number=orders['number'])
        orders_entries.append(new_entry)
    db.session.add_all(orders_entries)
    db.session.commit()


if __name__ == "__main__":
    app.run(debug=True)
'''
'''

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