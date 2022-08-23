import psycopg2
import dash_html_components as html
import dash_core_components as dcc
import dash_table
import pandas as pd

from DataBaseFilling.Config import config


def count_group_by_values_column(column, table):  # Test if column in table not list of columns

    conn = None

    if column in ["track_name", "artist_name", "track_name, artist_name", "artist_id"]:
        pass
    else:
        print("Please choose a column in this list : [track_name, artist_name, track_name, artist_name, artist_id]")
        return

    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT " + column + " FROM " + table)
        cur.execute("""SELECT 
                            """ + column + """,                     
                            COUNT(*) 
                        FROM """ + table + """
                        GROUP BY """ + column + """;""")
        print("The number of parts: ", cur.rowcount)

        count_group_by_elements_column = pd.DataFrame(cur.fetchall())

        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        count_group_by_elements_column = pd.DataFrame()
    finally:
        if conn is not None:
            conn.close()

    return count_group_by_elements_column


tracks_count = count_group_by_values_column(column="track_name, artist_name", table="streamingHistory")
tracks_count = tracks_count.rename(columns={0: "track_name", 1: "artist_name", 2: "nb_listening"})
print(tracks_count.head(5))
print(tracks_count.sort_values("nb_listening", ascending=False).head(5))

artists_count = count_group_by_values_column(column="artist_name", table="streamingHistory")
artists_count = artists_count.rename(columns={0: "artist_name", 1: "nb_listening"})
print(artists_count.sort_values("nb_listening", ascending=False).head(5))


def count_group_by_values_column_by_year(column, table, year):  # Test if column in table not list of columns

    conn = None

    if column in ["track_name", "artist_name", "track_name, artist_name", "artist_id"]:
        pass
    else:
        print("Please choose a column in this list : [track_name, artist_name, track_name, artist_name, artist_id]")
        return

    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT " + column + " FROM " + table)
        cur.execute("""SELECT 
                            """ + column + """,                     
                            COUNT(*) 
                        FROM """ + table + """
                        WHERE date_part('year', endtime)=""" + year + """
                        GROUP BY """ + column + """;""")
        print("The number of parts: ", cur.rowcount)

        count_group_by_elements_column_by_year = pd.DataFrame(cur.fetchall())

        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        count_group_by_elements_column_by_year = pd.DataFrame()
    finally:
        if conn is not None:
            conn.close()

    return count_group_by_elements_column_by_year


year = "2021"
tracks_count_by_year = count_group_by_values_column_by_year(column="track_name, artist_name",
                                                            table="streamingHistory",
                                                            year=year)

tracks_count_by_year = tracks_count_by_year.rename(columns={0: "track_name",
                                                            1: "artist_name",
                                                            2: "nb_listening"})
print(tracks_count_by_year.head())
print(tracks_count_by_year.sort_values("nb_listening", ascending=False).head(20))

artists_count_by_year = count_group_by_values_column_by_year(column="artist_name",
                                                            table="streamingHistory",
                                                            year=year)

artists_count_by_year = artists_count_by_year.rename(columns={0: "artist_name", 1: "nb_listening"})
print(artists_count_by_year.head())
print(artists_count_by_year.sort_values("nb_listening", ascending=False).head(20))


def app_layout():

    tracks_count = count_group_by_values_column(column="track_name, artist_name", table="streamingHistory")
    tracks_count = tracks_count.rename(columns={0: "track_name", 1: "artist_name", 2: "nb_listening"})

    artists_count = count_group_by_values_column(column="artist_name", table="streamingHistory")
    artists_count = artists_count.rename(columns={0: "artist_name", 1: "nb_listening"})

    dict_tracks_count_by_year = {year: count_group_by_values_column_by_year(column="track_name, artist_name",
                                                                            table="streamingHistory",
                                                                            year=year)
                                 for year in ["2020", "2021", "2022"]}
    dict_tracks_count_by_year = {key: value.rename(columns={0: "track_name",
                                                                1: "artist_name",
                                                                2: "nb_listening"})
                                 for key, value in dict_tracks_count_by_year.items()}

    dict_artists_count_by_year = {year: count_group_by_values_column_by_year(column="artist_name",
                                                                             table="streamingHistory",
                                                                             year=year)
                                  for year in ["2020", "2021", "2022"]}
    dict_artists_count_by_year = {key: value.rename(columns={0: "artist_name",
                                                             1: "nb_listening"})
                                  for key, value in dict_artists_count_by_year.items()}

    layout = html.Div([html.H1('Report musical', style={'textAlign': 'center'}),

                       dcc.Tabs(id="Reports", children=[
                           dcc.Tab(label='Report titres', children=[
                               html.Div([html.H1("Titres les plus écoutés", style={'textAlign': 'center'}),
                                         dash_table.DataTable(
                                             data=tracks_count.sort_values("nb_listening", ascending=False).head(20).to_dict('records'),
                                             columns=[{"name": str(i), "id": str(i)} for i in tracks_count.columns])
                                         ]),
                               html.Div([html.H1("Titre les plus écoutés par année", style={'textAlign': 'center'}),
                                         dcc.Tabs(id="Années titres", children=[
                                             dcc.Tab(label=year, children=[
                                                 html.Div([dash_table.DataTable(
                                                     data=dict_tracks_count_by_year[year].sort_values("nb_listening",
                                                                                                       ascending=False).to_dict(
                                                         'records'),
                                                     columns=[{"name": str(i), "id": str(i)}
                                                              for i in dict_tracks_count_by_year[year].columns]
                                                 )
                                                 ]),
                                             ])
                                             for year in ["2020", "2021", "2022"]
                                         ])
                                         ])
                           ]),
                           dcc.Tab(label='Report artistes', children=[
                               html.Div([html.H1("Artistes les plus écoutés", style={'textAlign': 'center'}),
                                         dash_table.DataTable(
                                             data=artists_count.sort_values("nb_listening", ascending=False).head(20).to_dict('records'),
                                             columns=[{"name": str(i), "id": str(i)} for i in artists_count.columns])
                                         ]),
                               html.Div([html.H1("Artistes les plus écoutés par année", style={'textAlign': 'center'}),
                                         dcc.Tabs(id="Années artistes", children=[
                                             dcc.Tab(label=year, children=[
                                                 html.Div([dash_table.DataTable(
                                                     data=dict_artists_count_by_year[year].sort_values("nb_listening", ascending=False).to_dict('records'),
                                                     columns=[{"name": str(i), "id": str(i)}
                                                              for i in dict_artists_count_by_year[year].columns]
                                                 )
                                                 ]),
                                             ])
                                             for year in ["2020", "2021", "2022"]
                                         ])
                                         ])
                           ])
                       ])
                       ])
    """
    """

    return layout
