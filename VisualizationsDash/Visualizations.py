import dash
import psycopg2
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output

from AppLayout import app_layout
from DataBaseFilling.Config import config


app = dash.Dash()
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([html.H1("Facebook Data Analysis", style={"textAlign": "center"}), dcc.Markdown('''
Welcome to my Plotly (Dash) Data Science interactive dashboard. In order to create this dashboard have been used two different datasets. The first one is the [Huge Stock Market Dataset by Boris Marjanovic](https://www.kaggle.com/borismarjanovic/price-volume-data-for-all-us-stocks-etfs)
and the second one is the [Facebook metrics Data Set by Moro, S., Rita, P., & Vala, B](https://archive.ics.uci.edu/ml/datasets/Facebook+metrics). This dashboard is divided in 3 main tabs. In the first one you can choose whith which other companies to compare Facebook Stock Prices to anaylise main trends.
Using the second tab, you can analyse the distributions each of the Facebook Metrics Data Set features. Particular interest is on how paying to advertise posts can boost posts visibility. Finally, in the third tab a Machine Learning analysis of the considered datasets is proposed. 
All the data displayed in this dashboard is fetched, processed and updated using Python (eg. ML models are trained in real time!).
''') ])
""",
    dcc.Tabs(id="tabs", children=[
        dcc.Tab(label='Stock Prices', children=[
html.Div([html.H1("Dataset Introduction", style={'textAlign': 'center'}),
dash_table.DataTable(
    id='table',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.iloc[0:5,:].to_dict("rows"),
),
    html.H1("Facebook Stocks High vs Lows", style={'textAlign': 'center', 'padding-top': 5}),
    dcc.Dropdown(id='my-dropdown',options=[{'label': 'Tesla', 'value': 'TSLA'},{'label': 'Apple', 'value': 'AAPL'},{'label': 'Facebook', 'value': 'FB'},{'label': 'Microsoft', 'value': 'MSFT'}],
        multi=True,value=['FB'],style={"display": "block", "margin-left": "auto", "margin-right": "auto", "width": "80%"}),
    dcc.Graph(id='highlow'),  dash_table.DataTable(
    id='table2',
    columns=[{"name": i, "id": i} for i in df.describe().reset_index().columns],
    data= df.describe().reset_index().to_dict("rows"),
),
    html.H1("Facebook Market Volume", style={'textAlign': 'center', 'padding-top': 5}),
    dcc.Dropdown(id='my-dropdown2',options=[{'label': 'Tesla', 'value': 'TSLA'},{'label': 'Apple', 'value': 'AAPL'},{'label': 'Facebook', 'value': 'FB'},{'label': 'Microsoft', 'value': 'MSFT'}],
        multi=True,value=['FB'],style={"display": "block", "margin-left": "auto", "margin-right": "auto", "width": "80%"}),
    dcc.Graph(id='volume'),
    html.H1("Scatter Analysis", style={'textAlign': 'center', 'padding-top': -10}),
    dcc.Dropdown(id='my-dropdown3',
                 options=[{'label': 'Tesla', 'value': 'TSLA'}, {'label': 'Apple', 'value': 'AAPL'},
                          {'label': 'Facebook', 'value': 'FB'}, {'label': 'Microsoft', 'value': 'MSFT'}],
                 value= 'FB',
                 style={"display": "block", "margin-left": "auto", "margin-right": "auto", "width": "45%"}),
    dcc.Dropdown(id='my-dropdown4',
                 options=[{'label': 'Tesla', 'value': 'TSLA'}, {'label': 'Apple', 'value': 'AAPL'},
                          {'label': 'Facebook', 'value': 'FB'}, {'label': 'Microsoft', 'value': 'MSFT'}],
                 value= 'AAPL',
                 style={"display": "block", "margin-left": "auto", "margin-right": "auto", "width": "45%"}),
  dcc.RadioItems(id="radiob", value= "High", labelStyle={'display': 'inline-block', 'padding': 10},
                 options=[{'label': "High", 'value': "High"}, {'label': "Low", 'value': "Low"} , {'label': "Volume", 'value': "Volume"}],
 style={'textAlign': "center", }),
    dcc.Graph(id='scatter')
], className="container"),
]),
dcc.Tab(label='Performance Metrics', children=[
html.Div([html.H1("Facebook Metrics Distributions", style={"textAlign": "center"}),
            html.Div([html.Div([dcc.Dropdown(id='feature-selected1',
                                             options=[{'label': i.title(), 'value': i} for i in
                                                      df2.columns.values[1:]],
                                             value="Type")],
                               style={"display": "block", "margin-left": "auto", "margin-right": "auto",
                                      "width": "80%"}),
                      ],),
            dcc.Graph(id='my-graph2'),
dash_table.DataTable(
    id='table3',
    columns=[{"name": i, "id": i} for i in df.describe().reset_index().columns],
    data= df.describe().reset_index().to_dict("rows"),
),
            html.H1("Paid vs Free Posts by Category", style={'textAlign': "center", 'padding-top': 5}),
     html.Div([
         dcc.RadioItems(id="select-survival", value=str(1), labelStyle={'display': 'inline-block', 'padding': 10},
                        options=[{'label': "Paid", 'value': str(1)}, {'label': "Free", 'value': str(0)}], )],
         style={'textAlign': "center", }),
     html.Div([html.Div([dcc.Graph(id="hist-graph", clear_on_unhover=True, )]), ]),
        ], className="container"),
]),
dcc.Tab(label='Machine Learning', children=[
html.Div([html.H1("Machine Learning", style={"textAlign": "center"}), html.H2("ARIMA Time Series Prediction", style={"textAlign": "left"}),
    dcc.Dropdown(id='my-dropdowntest',options=[{'label': 'Tesla', 'value': 'TSLA'},{'label': 'Apple', 'value': 'AAPL'},{'label': 'Facebook', 'value': 'FB'},{'label': 'Microsoft', 'value': 'MSFT'}],
                style={"display": "block", "margin-left": "auto", "margin-right": "auto", "width": "50%"}),
          dcc.RadioItems(id="radiopred", value="High", labelStyle={'display': 'inline-block', 'padding': 10},
                         options=[{'label': "High", 'value': "High"}, {'label': "Low", 'value': "Low"},
                                  {'label': "Volume", 'value': "Volume"}], style={'textAlign': "center", }),
    dcc.Graph(id='traintest'), dcc.Graph(id='preds'),
html.H2("Performance Metrics Regression Prediction", style={"textAlign": "left"}), html.P("In this example I used the Facebook Performance Metrics dataset to predict the number of likes I post can get. Training a Random Forest Regressor with 500 estimetors right now online lead an accuracy (%) in the Training set equal to: "),
    str(train_acc), html.P("In the Test set, was instead registred an accuracy (%) of:"), str(test_acc),
    html.P("In order to achieve these results, all the not a numbers (NaNs) have been eliminated, categorical data has been encoded and the data has been normalized. The R2 score has been used as metric for this exercise and a Train/Test split ratio of 70:30% was used.")],)
], className="container")
])
])"""

app.layout = app_layout()


if __name__ == '__main__':
    app.run_server(debug=True)
    #print(tracks_count.sort_values("nb_listening", ascending=False).head(15))
