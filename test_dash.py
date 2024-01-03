#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 20 10:10:51 2023

@author: lendler
"""

from dash import Dash, dcc, html, Input, Output, State, callback, no_update
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import re
from base64 import decodebytes, b64encode, b64decode
from io import BytesIO
import pyzbar.pyzbar
from PIL import Image, ExifTags, ImageDraw

app = Dash(__name__)

app.layout = html.Div([
    html.H6("Change the value in the text box to see callbacks in action!"),
    html.Div([
        "Input: ",
        dcc.Input(id='my-input', value='initial value', type='text')
    ]),
    html.Br(),
    html.Div([
        "Input2: ",
        dcc.Input(id='my-input2', value='initial value', type='text')
    ]),
    html.Div([
        "Barcode: ",
        dcc.Input(id='barcode', placeholder="barcode", type='text')
    ]),
    html.Div(id='my-output'),
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
    html.Div(id='image_div')

])


@callback(
    Output(component_id='my-output', component_property='children'),
    Input(component_id='my-input', component_property='value')
)
def update_output_div(input_value):
    return f'Output: {input_value}'


@callback(
    Output(component_id='my-input', component_property='value'),
    Input(component_id='my-input2', component_property='value')
)
def update_output_div2(input_value):
    return input_value


@app.callback(
    [Output("image_div", 'children'),
     Output(component_id='barcode', component_property='value')],
    Input("upload_component", 'contents'),
    State("barcode", 'value'),
)
def update_output(image_u, barcode):
    if not image_u:
        raise PreventUpdate
    elif not re.match('data:image/[a-zA-z0-9._-]*;base64', image_u):
        return dbc.Alert("not recognized as an image, try a jpeg", color="warning")
    #image = image_u.split(',')[1]
    image_data = re.sub('^data:image/.+;base64,', '', image_u)
    img = Image.open(BytesIO(b64decode(image_data)))
    bcode, img = read_barcode(img)
    if isinstance(bcode, dbc.Alert):
        return bcode, barcode
    img_b = BytesIO()
    img.save(img_b, format="JPEG")
    img_b = b64encode(img_b.getvalue()).decode("utf-8")
    return html.Img(src="data:image/jpg;base64," + img_b, width="25%"), bcode.decode('utf-8')


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


if __name__ == '__main__':
    app.run(debug=True)
