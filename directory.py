#import all libraries

import subprocess
import dash
from dash import Dash, html, dcc
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
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

#import the tkinter apps to add new wafers and chips from their respective files in the folder
from chipApp import WaferApp
from waferApp import WaferAdd

#opens the text for the tutorial page
tut = open("tutorial.txt", "r")

#functions to call the tkinter apps (will be used in Callbacks)
def add_new_chip_interface():
    root = tk.Tk()
    root.title("Wafer Drawing App")
    app = WaferApp(root)
    root.mainloop()
    
def add_new_wafer_interface():
    root = tk.Tk()
    root.title("Add New Wafer")
    app = WaferAdd(root)
    root.mainloop()

#column definitions for the data tables:

#wafers (once year is selected)
wcolumnDefs = [
    { 'field': 'ID' },
    { 'field': 'Type'},
    { 'field': 'Intended Use'},
    { 'field': 'Date Acquired'},
    { 'field': 'Summary'}
]
#wafers (when no year is selected)
gwcolumnDefs = [
    { 'field': 'Year' },
    { 'field': 'ID' },
    { 'field': 'Type'},
    { 'field': 'Intended Use'},
    { 'field': 'Date Acquired'},
    { 'field': 'Summary'}
]
#chips
ccolumnDefs = [
    { 'field': 'Chip ID' },
    { 'field': 'Owner' },
    { 'field': 'Device' },
]

#read dataframes for wafers and chips (point of improvement: make this one excel file with two sheets)
wdf = pd.read_excel(io='wafers.xlsx', sheet_name=None)['Sheet']
cdf = pd.read_excel(io='all_wafers.xlsx', sheet_name=None)['Sheet']

#initialize app (dbc.theme.CYBORG is the colour theme, CYBORG is the dark mode-ish thing that is active right now)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

app.title = "Wafer Directory"

# Sidebar styling
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "12rem",
    "padding": "1rem 0.5rem",
    "background-color": "#343a40",
    "color": "#ffffff",
    "font-size": "12px"
}

# Content styling
CONTENT_STYLE = {
    "margin-left": "14rem",
    "margin-right": "1rem",
    "padding": "1rem",
    "background-color": "#f8f9fa",
    "border-radius": "5px",
    "font-size": "12px"
}

# Sidebar layout
sidebar = html.Div(
    [
        #Pulls up logo from the assets folder, note the classNames, these are referring to the stylesheet
        html.Img(src="assets/qnllogo.jpeg", className="banner"),
        html.H2("QNL Wafer Directory", className="display-6", style={"color": "#ffffff", "font-size": "14px"}),
        dbc.Button('GitHub', id='button_plain', href = "https://github.com/dylan-burke/QNL-Wafer-Database"),
        html.Hr(style={"border-color": "#ffffff"}),
        dbc.Nav(
            [
                #Buttons between pages for wafer select and tutorial pages
                dbc.NavLink("Wafer Select", href="/", active="exact", className="nav-link text-white"),
                dbc.NavLink("How To Use", href="/page-1", active="exact", className="nav-link text-white"),
            ],
            vertical=True,
            pills=True,
        ),
        html.Br(),
        #Add new buttons
        dbc.Button('Add New Wafer', id='addNewWafer', color="primary", className="mb-2", style={"font-size": "12px", "width": "100%"}),
        dbc.Button('Add New Chip', id='addNewChip', color="primary", style={"font-size": "12px", "width": "100%"}),
    ],
    style=SIDEBAR_STYLE,
)

# Main content area
content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

# Callbacks for page content and interactions

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
#shows the relevant content based on which page you are viewing
def render_page_content(pathname):
    if pathname == "/":
        return html.Div([
            #year select
            html.H2("Select Year:", style={'text-align': 'left', 'font-size': "15px", 'color':'#000000'}),
            dcc.Dropdown(
                id='dropdownYear',
                options=[{'label': i, 'value': i} for i in wdf.Year.unique()],
                style={'color': '#000000', 'background-color': '#ffffff', 'border': '1px solid #ced4da', 'border-radius': '4px', 'font-size': '12px'}
            ),
            html.Br(),
            dbc.Card(
                dbc.CardBody(
                    [
                        html.H4("Wafer Details", className="card-title", style={"font-size": "14px"}),
                        html.Div(id='table', children=[], style={'font-family': "Open Sans"}),
                    ]
                ),
                className="mb-3",
                style={"max-height": "200px", "overflow-y": "auto"}
            ),
            html.H2("Selected Wafer:", style={'text-align': 'left', 'font-size': "12px", 'color':'#000000'}),
            html.H2(id="selected_wafer", style={"font-size": "14px", 'color':'#d47604'}),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.Div(id='dTable'),
                                ]
                            ),
                            className="mb-3",
                            style={"max-height": "500px", "overflow-y": "auto"}
                        ),
                        width=6
                    ),
                    dbc.Col(
                        dbc.Card(
                            dbc.CardBody(
                                [
                                    html.H4("Wafer Map", className="card-title", style={"font-size": "14px"}),
                                    html.Div(id='fig', style={'max-width': "500px", 'max-height': "500px", "margin": "auto"}),
                                ]
                            ),
                            className="mb-3"
                        ),
                        width=6
                    ),
                ],
                className="g-4"
            ),
        ])

    elif pathname == "/page-1":
        #tutorial page
        return html.Div([
            
            html.H2("How to Access the Directory", style={"color": "#000000"}),
            html.Br(),
            html.H6(tut.read(), style={"color": "#000000"})
            
        ])

    # If the user tries to reach a different page, return a 404 message (with QuackNL easter egg!)
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger", style={"font-size": "14px"}),
            html.Hr(),
            html.Img(src="assets/QuackNL_0.jpg.webp"),
        ],
        className="p-3 bg-light rounded-3",
    )

@app.callback(Output('table', 'children'), [Input('dropdownYear', 'value')])
def update_output(dropdownYear):
    if dropdownYear is None:
        table = dag.AgGrid(
            id="grid",
            rowData=wdf.to_dict("records"),
            columnDefs=gwcolumnDefs,
            columnSize="sizeToFit",
            dashGridOptions={"domLayout": "autoHeight"}
        )
        return table

    wdff = wdf.loc[wdf['Year'] == dropdownYear]

    table = dag.AgGrid(
        id="grid",
        rowData=wdff.to_dict("records"),
        columnDefs=wcolumnDefs,
        columnSize="sizeToFit",
        dashGridOptions={"domLayout": "autoHeight"}
    )
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

@app.callback(
    Output("dTable", "children"),
    Output("fig", "children"),
    Input("selected_wafer", "children")
)
def updateChipFigures(wafer):
    cdata = cdf.loc[cdf['Wafer ID'] == wafer]

    dtable = dag.AgGrid(
        id="get-started-example-basic",
        rowData=cdata.to_dict("records"),
        columnDefs=ccolumnDefs,
        dashGridOptions={"domLayout": "autoHeight"},
        style={"height": None},
        columnSize="sizeToFit"
    )

    df = cdata
    xC = df.apply(lambda row: np.array([row['x1'], row['x2'], row['x3'], row['x4']]), axis=1)
    yC = df.apply(lambda row: np.array([row['y1'], row['y2'], row['y3'], row['y4']]), axis=1)

    fig = go.Figure()
    ld = len(df)
    fig.update_xaxes(range=[0, 1])
    fig.update_yaxes(range=[0, 1])

    fig.add_shape(
        type="circle",
        xref="x", yref="y",
        x0=0, y0=0, x1=1, y1=1,
        line_color="White",
    )

    fig.update_layout(
        width=500,
        height=500,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        title_font=dict(size=16, color="#000000"),
        font=dict(color="#ffffff")
    )
    
    #change this if needed
    fig.update_layout(showlegend=False)
    
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)

    for i in range(ld):
        dff = df.iloc[i]
        xC = np.array([dff['x1'], dff['x2'], dff['x3'], dff['x4']])
        yC = np.array([dff['y1'], dff['y2'], dff['y3'], dff['y4']])
        fig.add_trace(go.Scatter(x=xC, y=yC, fill="toself", name=dff['Chip ID']))

    figure = html.Div([dcc.Graph(figure=fig)])

    return dtable, figure

@app.callback([Input("addNewWafer", "n_clicks")])
def handle_button_click(n_clicks):
    if n_clicks > 0:
        add_new_wafer_interface()
    return

@app.callback([Input("addNewChip", "n_clicks")])
def handle_button_click(n_clicks):
    if n_clicks > 0:
        add_new_chip_interface()
    return


if __name__ == "__main__":
    app.run_server(jupyter_mode="external", port=8889)

