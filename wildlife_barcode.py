#!/usr/bin/env python#
#-*- coding: utf-8 -*
# import sys
import re
import os.path
from base64 import b64encode, b64decode  # , decodebytes
from io import BytesIO
#import time

#import dash_auth
import dash
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
from dash import dcc
#import dash_core_components as dcc
#import dash_html_components as html
from dash import html
from dash.dependencies import Input, Output, State  # , MATCH
#from dash.exceptions import PreventUpdate
#import dash_table
#import json
import pandas as pd
import plotly.express as px
#import plotly.graph_objects as go
#import dash_trich_components as dtc
import sqlite3
from sqlite3 import Error
#from datetime import datetime as dt
#from dateutil.relativedelta import relativedelta
#from datetime import timedelta
#import dash_more_components as dmc

import pyzbar.pyzbar

#import get_image_meta
from PIL import Image, ExifTags, ImageDraw
from datetime import date
from datetime import datetime

f = open("pwd.txt").read().splitlines()
VALID_USERNAME_PASSWORD_PAIRS = {x[0]: x[1] for x in map(lambda i: i.split(), f) if len(x) == 2}

app = dash.Dash(suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.YETI, 'https://use.fontawesome.com/releases/v5.8.1/css/all.css'],
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
                )


# auth = dash_auth.BasicAuth(
# app,
# VALID_USERNAME_PASSWORD_PAIRS
# )
# for render
#server = app.server
app.title = "Wildlife"

navbar = dbc.NavbarSimple(
    children=[
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem(dbc.Button("Synopsis", id="open", n_clicks=0)),
                dbc.DropdownMenuItem("Page 2", href="/page-1"),
                dbc.DropdownMenuItem("Page 3", href="/page-2"),
            ],
            nav=True,
            in_navbar=True,
            style={"font-weight": "bold"},
            label="Menu",
        ),
    ],
    brand="Wildlife pathogen",
    brand_style={"float": "left", "font": dict(family='Franklin Gothic')},
    color="rgb(64,185,212)",
    dark=True,
    fluid=True
)

body = dbc.Row([
    dbc.Col(
        children=[
            dcc.Geolocation(id="geolocation"),
            html.Label("Sample ID"),
            dbc.Input(placeholder="Sample ID",
                      type="text",
                      id="sample_id", style={"width": "50%"}),
            html.Label("Date"),
            dcc.DatePickerSingle(id="date_picker", display_format="DD/MM/YYYY",
                                 style={"minWidth": "100%", "marginBottom": "10px"}),
            html.Label("Time"),
            dbc.Input(placeholder="Time",
                      type="text",
                      id="time",
                      style={"width": "50%"}),
            # html.Label("Geo position"),
            # dbc.InputGroup([
            # dbc.Input(placeholder="GPS", id = "geo_input"),
            # dbc.Button("Update", id="update_btn", color = "success"),
            # ]),
            html.Label("Species"),
            dcc.Dropdown(
                options=[
                    {"label": "deer", "value": "deer"},
                    {"label": "boar", "value": "boar"},
                    {"label": "lynx", "value": "lynx"},
                    {"label": "martes", "value": "martes"},
                ],
                placeholder="select...",
                id="species"
            ),
            html.Label("Sample from"),
            dcc.Dropdown(
                options=[
                    {"label": "cadaver", "value": "cadaver"},
                    {"label": "live animal", "value": "live animal"},
                ],
                placeholder="select...",
                id="sample_live"
            ),
            html.Label("Sample type"),
            dcc.Dropdown(
                options=[
                    {"label": "blood", "value": "blood"},
                    {"label": "faeces", "value": "faeces"},
                    {"label": "saliva", "value": "saliva"},
                    {"label": "other", "value": "other"},
                ],
                placeholder="select...",
                id="sample_type"
            ),
            html.Label("Symptoms"),
            dcc.Dropdown(
                options=[
                    {"label": "no symptoms", "value": "no symptoms"},
                    {"label": "with symptoms", "value": "with symptoms"},
                ],
                placeholder="select...",
                id="symptoms"
            ),
            dcc.Upload(id="upload_component",
                       multiple=False,
                       children=[
                           dbc.Button(
                               "Upload photos",
                               id="upload_btn",
                               color="primary",
                               style={"marginTop": "10px", "marginBottom": "10px"}
                           )
                       ]
                       ),
            dbc.Spinner(
                [html.Div(id="image_div")]
            ),
            dbc.Spinner([html.Div(id="map_div")]),
            dbc.Spinner([html.Div(id="submitted")]),
            dbc.Button("Submit form",
                       id="submit",
                       color="success",
                       style={"marginTop": "10px", "marginBottom": "10px"}
                       ),
            #dbc.Button("Upload", id = "upload_btn", children = [dcc.Upload(id = "upload_component", multiple = True)])
        ]
    )
]
)

app.layout = html.Div(
    [
        dcc.Location(id="url"),
        dcc.Store(id="barcode"),
        dcc.Store(id="image_filename"),
        dcc.Store(id="dummy"),
        navbar,
        dbc.Container(
            [body],
            className="mb-3",
        ),
    ]
)


@app.callback(
    Output("date_picker", "date"),
    Output("time", "value"),
    Input("submit", "n_clicks"),
)
def get_date(btn):
    today = date.today()
    now = datetime.now()
    # dd/mm/YY
    d1 = today.strftime("%m/%d/%Y")
    t1 = now.strftime("%H:%M:%S")
    return d1, t1


# @app.callback(
#     Output("sample_id", "value"),
#     Input("url", "search")
# )
# def get_url(sample_id):
#     # remove '?' if a start of URL
#     if sample_id.index("?") == 0:
#         sample_id = sample_id.replace("?", "", count="1")
#     return sample_id


@app.callback(
    Output("geolocation", "update_now"),
    Input("update_btn", "n_clicks")
)
def update_now(click):
    return True if click and click > 0 else False


@app.callback(Output("map_div", "children"), Input("coords", "data"))
def map(coords):
    data = []
    if coords is None:
        return None
    for cor in coords:
        data.append({"lat": cor[0], "lon": cor[1]})
    df = pd.DataFrame.from_records(data)
    print(df)
    fig = px.scatter_mapbox(
        df,
        mapbox_style="carto-positron",
        lat="lat",
        lon="lon",
        center={"lat": coords[0][0], "lon": coords[0][1]},
        zoom=12,
        #autosize=True
        #height=400,
    )
    fig.update_layout(height=250, width=250, margin={"l": 0, "r": 0, "b": 5, "t": 25})
    fig_map = dcc.Graph(figure=fig)
    return fig_map


def parse_contents(contents, fname):
    return html.Div([
        # HTML images accept base64 encoded strings in the same format
        # that is supplied by the upload
        html.Img(src=contents),
        #get_image_meta.image_coordinates(fname)
    ])


@app.callback(
    Output("sample_id", 'value'),
    Input("barcode", 'data'),
    #State("sample_id", "value")
)
def sample_id_from_barcode(barcode):
    if not barcode:
        raise PreventUpdate
    return barcode


@app.callback(
    Output("image_div", 'children'),
    Output("barcode", 'data'),
    Output("image_filename", 'data'),
    Input("upload_component", 'contents'),
    State("sample_id", "value"),
)
def update_output(img_u, sample_id):
    if not img_u:
        raise PreventUpdate
    elif not re.match('data:image/.+;base64', img_u):
        return dbc.Alert("not recognized as an image, try a jpeg", color="warning"), sample_id, None
    CURDIR = os.path.abspath(os.path.curdir)
    if not os.path.exists(CURDIR + "/wildlifedata") or not os.path.exists(CURDIR + "/wildlifedata/images"):
        os.mkdir(CURDIR + "/wildlifedata")
        os.mkdir(CURDIR + "/wildlifedata/images")
    elif not os.path.isdir(CURDIR + "/wildlifedata/images"):
        raise PreventUpdate
    img = re.sub('^data:image/.+;base64,', '', img_u)
    img = Image.open(BytesIO(b64decode(img)))
    bcode, img_a = read_barcode(img.copy())
    if isinstance(bcode, dbc.Alert):
        return bcode, sample_id, None
    img_b = BytesIO()
    img_a.save(img_b, format="JPEG")
    img_b = b64encode(img_b.getvalue()).decode("utf-8")
    bcode = bcode.decode('utf-8')
    himg = html.Img(src="data:image/jpg;base64," + img_b, width="25%")
    image_filename = CURDIR + "/wildlifedata/images/image_" + bcode + ".jpg"
    img.save(image_filename, format="JPEG")
    child = dbc.Card([
        dbc.CardBody([
            html.H5(os.path.basename(image_filename), className="card-title"),
            himg
        ])
    ])
    return dbc.Row([dbc.Col(child)]), bcode, image_filename


@app.callback(
    Output("submitted", "children"),
    Input("submit", "n_clicks"),
    State("sample_id", "value"),
    State("date_picker", "date"),
    State("time", "value"),
    State("species", "value"),
    State("sample_live", "value"),
    State("sample_type", "value"),
    State("symptoms", "value"),
    State("image_filename", "data"),
)
def save(n, sample_id, date, stime, species, sample_live, sample_type, symptoms, image_filename):
    #json_string = {"sample_id":sample_id, "date":date, "time":time, "species":species, "sample_live":sample_live, "symptoms":symptoms, "coords":", ".join(coords), "image_filenames":", ".join(image_filenames)}
    if n == 0 or not sample_id:
        raise PreventUpdate
    CURDIR = os.path.abspath(os.path.curdir)
    if not os.path.exists(CURDIR + "/wildlifedata") or not os.path.exists(CURDIR + "/wildlifedata/images"):
        os.mkdir(CURDIR + "/wildlifedata")
        os.mkdir(CURDIR + "/wildlifedata/images")
    elif not os.path.isdir(CURDIR + "/wildlifedata"):
        raise PreventUpdate
    bigdict = {
        "sample_id": sample_id,
        "date": date,
        "time": stime,
        "species": species,
        "sample_live": sample_live,
        "symptoms": symptoms,
        #"coords": coords,
        "image_filename": image_filename
    }
    json_string = str(bigdict)
    if sample_id is None or len(sample_id) == 0:
        return dbc.Alert("Sample ID " + str(sample_id) + " is empty", color="warning")
    f = open(CURDIR + "/wildlifedata/" + sample_id + ".json", "w")
    f.write(json_string)
    f.close()
    #DB update
    dbname = CURDIR + "/wildlifedata/wd_sqlite.db"
    tab_name = "wildlife_data"
    con = get_db_connection(dbname, tab_name=tab_name)
    if not isinstance(con, sqlite3.Connection):
        return dbc.Alert("DB problem" + con, color="error")
    tab_cols = con.execute(f"PRAGMA table_info('{tab_name}')").fetchall()
    tab_cols = [x[1] for x in tab_cols]
    # check database table to see whether columns and big dict are similar
    if not all([x in bigdict.keys() for x in tab_cols]):
        return dbc.Alert("Some database columns missing in bigdict!", color="error")
    elif not all([x in tab_cols for x in bigdict.keys()]):
        return dbc.Alert("Some bigdict fields missing in database table!", color="error")
    #vals = [tab_name]
    #vals.extend([bigdict[x] for x in tab_cols])
    try:
        curs = con.cursor()
        curs.execute(f"INSERT INTO {tab_name} VALUES ( ?" + ", ?" * (len(tab_cols) - 1) + " )",
                     [bigdict[x] for x in tab_cols])
        con.commit()
    except Error as e:
        return dbc.Alert("DB submission problem:" + e, color="error")
    con.close()
    missing = []
    for key, val in bigdict.items():
        if val is None:
            missing.append(key)
    if len(missing) == 0:
        return dbc.Alert("Sample " + sample_id + " has been submitted.", color="success")
    else:
        return dbc.Alert("Warning: following fields were empty: " + ",".join(missing), color="warning")


def get_db_connection(dbname,
                      tab_name="wildlife_data",
                      col_names=["sample_id", "date", "time", "species", "sample_live", "symptoms", "image_filename"]):
    con = None
    try:
        con = sqlite3.connect(dbname)
    except Error as e:
        return "DB connection error" + e
    curs = con.cursor()
    tables = curs.execute("SELECT name FROM sqlite_master WHERE TYPE = 'table'").fetchall()
    if len(tables) == 0 or not(tab_name in [x[0] for x in tables]):
        # add table
        curs.execute(f"CREATE TABLE {tab_name}({','.join(col_names)})")
        con.commit()
    curs.close()
    return con


def read_barcode(img, code=[pyzbar.pyzbar.ZBarSymbol.CODE128]):
    # for testing
    # img_mb = Image.open("test_barcode_multi.jpg")
    # img_cb = Image.open('test_barcode_cartridge.jpg')
    bcodes = pyzbar.pyzbar.decode(img, code)
    if len(bcodes) == 0:
        return dbc.Alert("Warning: No barcodes identified!"), img
    elif len(bcodes) > 1:
        return dbc.Alert("Warning: Multiple barcodes identified!"), img
    bcoords = [bcodes[0].rect.left, bcodes[0].rect.top,
               bcodes[0].rect.left + bcodes[0].rect.width,
               bcodes[0].rect.top + bcodes[0].rect.height]
    img_draw = ImageDraw.Draw(img)
    img_draw.rectangle(bcoords, outline="red", width=5)
    return bcodes[0].data, img


def get_image_metadata(img):
    exif_d = img.getexif()
    if len(exif_d) == 0:
        return None
    return({ExifTags.TAGS[x]: exif_d[x] for x in ExifTags.TAGS if x in exif_d})


def get_gps_coords(img):
    """gets GPS longitude and latitude from image exif data using pillow >= 10.0.0"""
    #img = Image.open(img)
    exif_d = None
    try:
        exif_d = img.getexif()
        if ExifTags.IFD.GPSInfo in exif_d:
            gps_d = exif_d.get_ifd(ExifTags.IFD.GPSInfo)
    except:
        return None
    tags = ["GPSLatitude", "GPSLatitudeRef", "GPSLongitude", "GPSLongitudeRef"]
    tags = {x: int(ExifTags.GPS[x]) for x in tags}
    gps_d = {x: gps_d[tags[x]] for x in tags if tags[x] in gps_d}
    if not ("GPSLatitude" in gps_d and "GPSLongitude" in gps_d):
        return None
    gps_coords = [0, 0]
    if len(gps_d["GPSLatitude"]) == 3:
        gps_coords[0] = gps_d["GPSLatitude"][0] + gps_d["GPSLatitude"][1] / 60.0 + gps_d["GPSLatitude"][2] / 3600
        gps_coords[1] = gps_d["GPSLongitude"][0] + gps_d["GPSLongitude"][1] / 60.0 + gps_d["GPSLongitude"][2] / 3600
    if "GPSLatitudeRef" in gps_d:
        if gps_d["GPSLatitudeRef"] == "S":
            gps_coords[0] *= -1
        if gps_d["GPSLongitudeRef"] == "W":
            gps_coords[1] *= -1
    return gps_coords


#height=800, width = 800,
if __name__ == "__main__":
    app.run_server(debug=True, dev_tools_ui=True, dev_tools_props_check=True, host='0.0.0.0')
