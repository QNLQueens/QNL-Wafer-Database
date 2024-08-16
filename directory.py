import dash
from dash import Dash, html, dcc, dash_table
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, filedialog
import os
import openpyxl
import pandas as pd
import threading
from dash.dependencies import Input, Output, State
import dash_ag_grid as dag
import json
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.lines as lines
import matplotlib.patches as patches
import math
import numpy as np
from chipApp import WaferApp
from waferApp import new_wafer
import plotly.graph_objects as go

def add_new_chip_interface():
    root = tk.Tk()
    root.title("Wafer Drawing App")
    app = WaferApp(root)
    root.mainloop()
    
wcolumnDefs = [
    { 'field': 'ID' },
    { 'field': 'Type'},
    { 'field': 'Intended Use'},
    { 'field': 'Date Acquired'},
    { 'field': 'Summary'}
]

gwcolumnDefs = [
    { 'field': 'Year' },
    { 'field': 'ID' },
    { 'field': 'Type'},
    { 'field': 'Intended Use'},
    { 'field': 'Date Acquired'},
    { 'field': 'Summary'}
]

ccolumnDefs = [
    { 'field': 'Chip ID' },
    { 'field': 'Owner' },
    { 'field': 'Device' },
]

wdf = pd.read_excel(io ='wafers.xlsx', sheet_name=None); wdf = wdf['Sheet']
cdf = pd.read_excel(io ='all_wafers.xlsx', sheet_name=None); cdf = cdf['Sheet']
app = dash.Dash(__name__,suppress_callback_exceptions=True)

app.title = "Wafer Directory"


#layout

app.layout = html.Div([
    html.Div([
        html.H2("Wafer Directory"),
        html.Img(src="assets/qnllogo.jpeg")
    ], className = "banner"),
    
    html.Button('Add New Wafer', id='addNewWafer', className = "button"), html.Br(),  
    
    html.H2("Select Year:", style = {'text-align':'left', 'font-size': "150%"}),
    dcc.Dropdown(id='dropdownYear', options=[
        {'label': i, 'value': i} for i in wdf.Year.unique()
    ]), html.Br(),
    
    html.Div(id='table', children=[], style = {'font-family': "Open Sans"}), html.Br(),
    
    html.H2("Selected Wafer:", style = {'text-align':'left', 'font-size': "150%"}),
    html.H2(id="selected_wafer"),
    html.Br(),
    html.Button('Add New Chip', id='addNewChip', className = "button"), 
    html.Br(),
    
    html.Div([html.Div(id='dTable', className = "six columns"), 
              html.Div(id= 'fig', className = "six columns")], className = "row")

])




#callbacks

@app.callback(
    dash.dependencies.Output('table', 'children'),
    [dash.dependencies.Input('dropdownYear', 'value')])

def update_output(dropdownYear):
    if dropdownYear is None:
        table = dag.AgGrid(id="grid", rowData=wdf.to_dict("records"), 
                        columnDefs=gwcolumnDefs, columnSize="sizeToFit", dashGridOptions = {"domLayout": "autoHeight"})
        return table

    wdff = wdf.loc[wdf['Year'] == dropdownYear]
    
    table = dag.AgGrid(id="grid", rowData=wdff.to_dict("records"), 
                      columnDefs=wcolumnDefs, columnSize="sizeToFit",dashGridOptions = {"domLayout": "autoHeight"})
    return table


@app.callback(
    Output("selected_wafer", "children"),
    Input("grid", "cellClicked")
)
def display_cell_clicked_on(cell):
    if cell:
        wafer = cell['value']
    else:
        wafer = "None"
    return wafer

@app.callback(Output("dTable", "children"), Output("fig", "children"),
              [Input("selected_wafer", "children")])

def updateChipFigures(wafer):
    cdata = cdf.loc[cdf['Wafer ID'] == wafer]
    
    dtable = dag.AgGrid(id="get-started-example-basic", rowData=cdata.to_dict("records"), columnDefs = ccolumnDefs,
                     dashGridOptions = {"domLayout": "autoHeight"}, style = {"height": None}, columnSize="sizeToFit")
    
    df = cdata
    xC = df.apply(lambda row: np.array([row['x1'], row['x2'], row['x3'], row['x4']]), axis=1)
    yC = df.apply(lambda row: np.array([row['y1'], row['y2'], row['y3'], row['y4']]), axis=1)

    fig = go.Figure()
    ld = len(df)
    fig.update_xaxes(range=[0, 1])
    fig.update_yaxes(range=[0, 1])

    fig.add_shape(type="circle",
        xref="x", yref="y",
        x0=0, y0=0, x1=1, y1=1,
        line_color="Black",
    )

    fig.update_layout(width=1000, height=1000)

    for i in range(ld):
        dff = df.iloc[i]
        xC = np.array([dff['x1'], dff['x2'], dff['x3'], dff['x4']])
        yC = np.array([dff['y1'], dff['y2'], dff['y3'], dff['y4']])
        fig.add_trace(go.Scatter(x=xC, y=yC, fill="toself", name = dff['Chip ID']))

        
    figure = html.Div([dcc.Graph(figure= fig)])
    
    return dtable, figure


@app.callback([Input("addNewWafer", "n_clicks")])

def handle_button_click(n_clicks):
    if n_clicks > 0:
        subprocess.Popen(["python", "waferApp.py"])
    return

@app.callback([Input("addNewChip", "n_clicks")])

def handle_button_click(n_clicks):
    if n_clicks > 0:
        threading.Thread(target=add_new_chip_interface).start()
    return

if __name__ == '__main__':
    app.run(jupyter_mode="external", port = 8061, debug = True)
