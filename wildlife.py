#!/usr/bin/env python# 
#-*- coding: utf-8 -*
import sys
#import dash_auth
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, MATCH
#from dash.exceptions import PreventUpdate
#import dash_table
#import json
import pandas as pd
import plotly.express as px
#import plotly.graph_objects as go
#import dash_trich_components as dtc
#import sqlite3
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from datetime import timedelta
#import dash_more_components as dmc

import time
#import datatable
#import dash_bio as dashbio

import os.path
from os import path

import calendar
#from lollipop import get_lollipop
#import pillow
import io
from base64 import decodebytes

#import get_image_meta
from PIL import Image, ExifTags
from datetime import date
from datetime import datetime

f = open("pwd.txt").read().splitlines()
VALID_USERNAME_PASSWORD_PAIRS = { x[0]: x[1] for x in map(lambda i: i.split(), f) if len(x) == 2}

app = dash.Dash(	suppress_callback_exceptions = True, 
					external_stylesheets=[dbc.themes.YETI, 'https://use.fontawesome.com/releases/v5.8.1/css/all.css'],
					meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
				)



# auth = dash_auth.BasicAuth(
	# app,
	# VALID_USERNAME_PASSWORD_PAIRS
# )
# for render
#server = app.server
app.title="Wildlife"

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
								style = {"font-weight":"bold"},
								label="Menu",
				),
			],
			brand="Wildlife pathogen",
			brand_style = {"float":"left", "font":dict(family='Franklin Gothic')},
			color="rgb(64,185,212)",
			
			dark=True,
			fluid = True,
		)

body = 	dbc.Row([
			dbc.Col(
					children = [
								dcc.Geolocation(id="geolocation"),
								html.Label("Sample ID"),
								dbc.Input(placeholder="Sample ID", 
									type="text", 
									id = "sample_id", style={"width":"50%"}),
								html.Label("Date"),
								dcc.DatePickerSingle(id = "date_picker", display_format = "DD/MM/YYYY", style = {"minWidth":"100%", "marginBottom":"10px"}),
								html.Label("Time"),
								dbc.Input(placeholder="Time", 
									type="text", 
									id = "time",
									style={"width":"50%"}),
								# html.Label("Geo position"),
								# dbc.InputGroup([
									# dbc.Input(placeholder="GPS", id = "geo_input"),
									# dbc.Button("Update", id="update_btn", color = "success"),
								# ]),
								
								html.Label("Species"),
								dcc.Dropdown(options=[
														{"label":"deer", "value":"deer"},
														{"label":"boar", "value":"boar"},
														{"label":"lynx", "value":"lynx"},
														{"label":"martes", "value":"martes"},
											],
											placeholder = "select...",
											id = "species"
								),
								html.Label("Sample from"),
								dcc.Dropdown(options=[
														{"label":"cadaver", "value":"cadaver"},
														{"label":"live animal", "value":"live animal"},
														
											],
											placeholder = "select...",
											id = "sample_live"
								),
								html.Label("Sample type"),
								dcc.Dropdown(options=[
														{"label":"blood", "value":"blood"},
														{"label":"faeces", "value":"faeces"},
														{"label":"saliva", "value":"saliva"},
														{"label":"other", "value":"other"},
											],
											placeholder = "select...",
											id = "sample_type"
								),
								html.Label("Symptoms"),
								dcc.Dropdown(options=[
														{"label":"no symptoms", "value":"no symptoms"},
														{"label":"with symptoms", "value":"with symptoms"},
														
											],
											placeholder = "select...",
											id = "symptoms"
								),
								dcc.Upload(id = "upload_component", multiple = True, children = [dbc.Button("Upload photos", id = "upload_btn", color = "primary", style ={"marginTop":"10px","marginBottom":"10px"})]),
								dbc.Spinner([html.Div(id = "image_div")]),
								dbc.Spinner([html.Div(id = "map_div")]),
								dbc.Spinner([html.Div(id = "submitted")]),
								dbc.Button("Submit form", id = "submit", color = "success", style ={"marginTop":"10px","marginBottom":"10px"}),

								#dbc.Button("Upload", id = "upload_btn", children = [dcc.Upload(id = "upload_component", multiple = True)])
								
							
					]
			)
		
			], 
		)



app.layout = html.Div(
	[
		dcc.Location(id="url"),
		dcc.Store(id="coords"),
		dcc.Store(id="image_filenames"),
		dcc.Store(id="dummy"),
		navbar,
		dbc.Container([
			body
			], 
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

@app.callback(Output("sample_id","value"), Input("url","search"))
def get_url(sample_id):
	return sample_id.replace("?","")

@app.callback(Output("geolocation", "update_now"), Input("update_btn", "n_clicks"))
def update_now(click):
    return True if click and click > 0 else False

@app.callback(Output("map_div","children"),Input("coords","data"))
def map(coords):
	data = []
	for cor in coords:
		data.append({"lat":cor[0], "lon":cor[1]})
	df = pd.DataFrame.from_records(data)
	print(df)
	fig = fig=px.scatter_mapbox(df,
		mapbox_style = "carto-positron",
		lat = "lat",
		lon = "lon",
		center={"lat":coords[0][0], "lon": coords[0][1]},
		zoom = 12,
		#autosize=True
		#height=400,
		)
	fig.update_layout(height=250,margin = {"l":0, "r":0, "b":5, "t":25})
	fig_map = dcc.Graph(figure = fig)
	return fig_map

	# fig_map = dcc.Graph(figure = fig)
	
	
	
# @app.callback(
	# Output("date_picker", "date"),
	# Output("time", "value"),
	# Output("map_div","children"),
	# Output("geo_input","value"),
	# Input("geolocation", "local_date"),
	# Input("geolocation", "position"),
# )
# def display_output(date, pos):
	# print(date, pos)
	# date_f= date.split(",")[0]
	# time = date.split(",")[1]
	
	# df = pd.DataFrame.from_dict({"lat":[pos['lat']],"lon":[pos['lon']]})
	
	# fig = fig=px.scatter_mapbox(df,
			# mapbox_style = "carto-positron",
			# lat = "lat",
			# lon = "lon",
			# center={"lat":pos['lat'], "lon": pos['lon']},
			# zoom = 12,
			# #autosize=True
			# #height=400,
			# )
	# fig.update_layout(height=250,margin = {"l":0, "r":0, "b":5, "t":25})
		


	# fig_map = dcc.Graph(figure = fig)
	# fig_map = None
	
	# return date_f, time, fig_map, "lat: "+str(pos["lat"])+" lon: "+str(pos["lon"])

def parse_contents(contents, fname):
	return html.Div([

		# HTML images accept base64 encoded strings in the same format																														 
		# that is supplied by the upload																																					   
		html.Img(src=contents),
		#get_image_meta.image_coordinates(fname)
		
	])

@app.callback(Output("image_div", 'children'),
			Output("coords", 'data'),
			Output("image_filenames", 'data'),
			  [Input("upload_component", 'contents')])
def update_output(images):
	if not images:
		return
	
	image_filenames = []
	for i, image_str in enumerate(images):
		image_filenames.append("/home/ptriska/Desktop/wildlife/images/image_"+str(i)+".jpg")
		
		image = image_str.split(',')[1]
		data = decodebytes(image.encode('ascii'))
		with open("/home/ptriska/Desktop/wildlife/images/image_"+str(i)+".jpg", "wb") as f:
			f.write(data)
	items = []
	children = []
	coords = []
	for i, fname in zip(images, image_filenames):
		coords.append(get_gps_coords(fname))
		children.append(dbc.Card([ dbc.CardBody([
													html.H5(get_image_meta.image_metadata(fname), className="card-title"),
													html.Img(src = i)
												])
												
								]))
		#items.append({"alt":"no image", "key":fname, "src":fname, "caption": get_image_meta.image_coordinates(fname)})
		items.append({"src":fname})
		
		#children.append(parse_contents(i, fname))
	
	return dbc.CardColumns(children), coords, image_filenames
	#print("Chlen!!! ", len(children))
	#return dbc.Carousel(items = items)
	# return dtc.Carousel(children = children,
							# slides_to_scroll=1,
							# swipe_to_slide=True,
							# autoplay=False,
							# speed=1000,
						# #	variable_width=True,
							# center_mode=True
						# )

@app.callback(
				Output("submitted","children"),
				Input("submit","n_clicks"),
				State("sample_id","value"),
				State("date_picker","value"),
				State("time", "value"),
				State("species","value"),
				State("sample_live","value"),
				State("sample_type","value"),
				State("symptoms","value"),
				State("coords", "data"),
				State("image_filenames","data"),
				
)

def save(n, sample_id, date, time, species, sample_live, sample_type, symptoms, coords, image_filenames):
	#json_string = {"sample_id":sample_id, "date":date, "time":time, "species":species, "sample_live":sample_live, "symptoms":symptoms, "coords":", ".join(coords), "image_filenames":", ".join(image_filenames)}
	bigdict = {"sample_id":sample_id, "date":date, "time":time, "species":species, "sample_live":sample_live, "symptoms":symptoms, "coords":coords, "image_filenames":image_filenames}
	json_string = str(bigdict)

	f = open(sample_id+".json", "w")
	f.write(json_string)
	f.close()
	missing = []
	for key, val in bigdict.items():
		if val == None:
			missing.append(key)
	if len(missing)==0:
		return dbc.Alert("Sample "+sample_ID+" has been submitted.", color="success")
	else:
		return dbc.Alert("Warning: following fields were empty: "+",".join(missing), color="warning")


def get_gps_coords(img):
    """gets GPS longitude and latitude from image exif data using pillow >= 10.0.0"""
    img = Image.open(img)
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
