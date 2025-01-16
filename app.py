#import all libraries
import dash
from dash import Dash, html, dcc
import os
import pandas as pd
from dash.dependencies import Input, Output, State
import dash_ag_grid as dag
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.lines as lines
import matplotlib.patches as patches
import numpy as np
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from database import *


# Function to load wafer IDs
def load_wafer_ids():
    con = load_most_recent()
    wafers = read_database(con, 'wafers')
    wafer_ids = wafers['Wafer_ID'].execute().values
    return wafer_ids

#opens the text for the tutorial page
tut = open("tutorial.txt", "r")

#column definitions for the data tables:
#wafers (once year is selected)
wcolumnDefs = [
    { 'field': 'Wafer_ID' },
    { 'field': 'Type'},
    { 'field': 'Intended_Use'},
    { 'field': 'Date_Acquired'},
    { 'field': 'Summary'},
    { 'field': 'Origin'},
    { 'field': 'Substrate'},
    { 'field': 'Quality'}
]
#wafers (when no year is selected)
gwcolumnDefs = [
    { 'field': 'Year' },
    { 'field': 'Wafer_ID' },
    { 'field': 'Type'},
    { 'field': 'Intended_Use'},
    { 'field': 'Date_Acquired'},
    { 'field': 'Summary'},
    { 'field': 'Origin'},
    { 'field': 'Substrate'},
    { 'field': 'Quality'}
]
#chips
ccolumnDefs = [
    { 'field': 'Chip_ID' },
    { 'field': 'Owner' },
    { 'field': 'Device' },
]

#initialize app (dbc.theme.CYBORG is the colour theme, CYBORG is the dark mode-ish thing that is active right now)
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.config.suppress_callback_exceptions=True

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
        dbc.Button('GitHub', id='button_plain', href = "https://github.com/QNLQueens/QNL-Wafer-Database"),
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


# Layout for the edit modal
modal_edit = dbc.Modal([
    dbc.ModalHeader(dbc.ModalTitle("Edit Wafer Data")),
    dbc.ModalBody([
        dbc.Label("Select Wafer ID"),
        dcc.Dropdown(
            id="edit-modal-wid-dropdown",
            options=[{"label": wid, "value": wid} for wid in load_wafer_ids()],
            placeholder="Select a Wafer ID",
            value=None,
            style={'color': '#000000'}
        ),
        html.Hr(),

        dbc.Row([
            dbc.Col([dbc.Label("Wafer ID"), dbc.Input(id="edit-modal-wid-input", type="text")]),
            dbc.Col([dbc.Label("Year"), dbc.Input(id="edit-modal-year-input", type="number", min=2015, max=2025)])
        ], className="mb-3"),

        dbc.Row([
            dbc.Col([dbc.Label("Wafer Type"), dcc.Dropdown(id="edit-modal-type-dropdown", 
                                                             options=[{"label": t, "value": t} for t in ["101", "100", "Quarter"]])]),
            dbc.Col([dbc.Label("Date Acquired"), dbc.Input(id="edit-modal-date-input", type="text", placeholder="MM/DD")])
        ], className="mb-3"),

        dbc.Row([
            dbc.Col([dbc.Label("Created At"), dcc.Dropdown(id="edit-modal-origin-dropdown", 
                                                             options=[{"label": loc, "value": loc} for loc in ["NFK", "NRC"]])]),
            dbc.Col([dbc.Label("Substrate"), dcc.Dropdown(id="edit-modal-substrate-dropdown", 
                                                           options=[{"label": sub, "value": sub} for sub in ["InP", "GaAs"]])])
        ], className="mb-3"),

        dbc.Row([
            dbc.Col([dbc.Label("Quality"), dcc.Dropdown(id="edit-modal-quality-dropdown", 
                                                         options=[{"label": q, "value": q} for q in ["Good", "Bad"]])])
        ], className="mb-3"),

        dbc.Row([
            dbc.Col([dbc.Label("Intended Use"), dbc.Input(id="edit-modal-intuse-input", type="text")]),
            dbc.Col([dbc.Label("Summary"), dbc.Input(id="edit-modal-summary-input", type="text")])
        ], className="mb-3"),

        dbc.Button("Submit", id="edit-modal-submit-button", color="success", className="mt-3")
    ]),
    dbc.ModalFooter(
        dbc.Button("Close", id="edit-modal-close", className="ms-auto", n_clicks=0)
    )
], id="edit-modal", is_open=False, keyboard=False, backdrop="static",
                       style={'color': '#ffffff', 'border': '1px solid #ced4da', 'border-radius': '4px', 'font-size': '12px'})



app.layout = html.Div([dcc.Location(id="url"), 
                       sidebar, 
                       content,
                       modal_edit])

# Callbacks for page content and interactions

@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
#shows the relevant content based on which page you are viewing
def render_page_content(pathname):
    con = load_most_recent()
    wdf = read_database(con, 'wafers').execute()
    if pathname == "/":
        app.layout = html.Div([
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
            dbc.Button('Edit Wafer', id='editWafer', color="primary", className="mb-2", style={"font-size": "12px", "width": "10%"}),
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
            modal_edit
        ])
        return app.layout

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

# Callbacks
@app.callback(
    Output("edit-modal", "is_open"),
    [Input("editWafer", "n_clicks"), 
     Input("edit-modal-close", "n_clicks")],
    [State("edit-modal", "is_open")]
)
def edit_modal_toggle(open_clicks, close_clicks, is_open):
    """
    Toggles the state of a modal window based on click events.

    Args:
        open_clicks (int): The number of times the open button has been clicked.
        close_clicks (int): The number of times the close button has been clicked.
        is_open (bool): The current state of the modal window (True if open, False if closed).

    Returns:
        bool: The new state of the modal window (True if it should be open, False if it should be closed).
    """
    if open_clicks or close_clicks:
        return not is_open
    return is_open

@app.callback(
    [Output("edit-modal-wid-input", "value"),
     Output("edit-modal-year-input", "value"),
     Output("edit-modal-type-dropdown", "value"),
     Output("edit-modal-date-input", "value"),
     Output("edit-modal-origin-dropdown", "value"),
     Output("edit-modal-substrate-dropdown", "value"),
     Output("edit-modal-quality-dropdown", "value"),
     Output("edit-modal-intuse-input", "value"),
     Output("edit-modal-summary-input", "value")],
    [Input("edit-modal-wid-dropdown", "value"), Input('selected_wafer', 'children')],
    [State('edit-modal', 'is_open')]
)
def edit_modal_update_fields(selected_wid, selected_wafer, is_open):
    """ 
    Updates the fields of the edit modal based on the selected wafer ID.
    
    Args:
        selected_wid (str): The ID of the selected wafer.
        selected_wafer (str): The wafer selected by the user.
        is_open (bool): A flag indicating whether the modal is open.
    Returns:
        tuple: A tuple containing the wafer details in the following order:
            - Wafer_ID (str or None)
            - Year (str or None)
            - Type (str or None)
            - Date_Acquired (str or None)
            - Origin (str or None)
            - Substrate (str or None)
            - Quality (str or None)
            - Intended_Use (str or None)
            - Summary (str or None)
            If the wafer ID is not found, returns a tuple of Nones.
"""

    if not is_open and selected_wafer is not None:
        selected_wid = selected_wafer
    if selected_wid in load_wafer_ids():
        con = load_most_recent()
        # Replace this logic with your database fetching code
        wafers = read_database(con, 'wafers') 
        data = wafers.filter([wafers['Wafer_ID'] == selected_wid]).execute()
        return (data['Wafer_ID'].values[0], 
                data['Year'].values[0], 
                data['Type'].values[0], 
                data['Date_Acquired'].values[0], 
                data['Origin'].values[0], 
                data['Substrate'].values[0], 
                data['Quality'].values[0], 
                data['Intended_Use'].values[0], 
                data['Summary'].values[0])
        
    return (None, None, None, None, None, None, None, None, None)

@app.callback(
    [Input("edit-modal-submit-button", "n_clicks"),
     Input("edit-modal-close", "n_clicks"),
     Input("edit-modal-wid-input", "value"),
     Input("edit-modal-year-input", "value"),
     Input("edit-modal-type-dropdown", "value"),
     Input("edit-modal-date-input", "value"),
     Input("edit-modal-origin-dropdown", "value"),
     Input("edit-modal-substrate-dropdown", "value"),
     Input("edit-modal-quality-dropdown", "value"),
     Input("edit-modal-intuse-input", "value"),
     Input("edit-modal-summary-input", "value")
     ],
)
def edit_modal_submit_data(n_clicks_submit, n_clicks_close, wid, year, wtype, date, create, substrate, quality, intuse, summary): 
    """
    Handles the submission and closing of the edit modal form.

    Args:
        n_clicks_submit (int): Number of times the submit button has been clicked.
        n_clicks_close (int): Number of times the close button has been clicked.
        wid (str): Wafer ID.
        year (int): Year of the wafer.
        wtype (str): Type of the wafer.
        date (str): Date of the wafer creation.
        create (str): Creator of the wafer.
        substrate (str): Substrate used for the wafer.
        quality (str): Quality of the wafer.
        intuse (str): Intended use of the wafer.
        summary (str): Summary of the wafer details.
    Returns:
        None
    """
    
    if n_clicks_submit:
        con = load_most_recent()
        wafers = read_database(con, 'wafers')
        new_row = pd.DataFrame([[wid, year, wtype, intuse, date, summary, create, substrate, quality]], columns=wafers.columns)
        update_database(con, 'wafers', new_row)
    if n_clicks_close:
        return 


@app.callback(Output('table', 'children'), [Input('dropdownYear', 'value'), Input('edit-modal-close', 'n_clicks')])
def update_output(dropdownYear, n_clicks):
    """
    Updates the AgGrid table display based on the selected year.
    This function retrieves wafer data from the database and filters it by year if specified.
    It creates and returns an AgGrid table component with the filtered or unfiltered data.
    
    Args:
        dropdownYear (int or None): The year to filter the wafer data by. If None, shows all years.
        n_clicks (int): Number of button clicks (not used in current implementation).
    Returns:
        dash_ag_grid.AgGrid: An AgGrid table component populated with the wafer data.
    
    Notes:
        The function uses two different column definitions:
        - gwcolumnDefs: for displaying all wafer data
        - wcolumnDefs: for displaying year-filtered data
    """
    con = load_most_recent()
    wdf = read_database(con, 'wafers').execute()
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
        con = load_most_recent()
        wdf = read_database(con, 'wafers').execute()
        wafer = wdf.loc[cell['rowIndex']]['Wafer_ID']
    else:
        wafer = "None"
    return wafer


@app.callback(
    Output("dTable", "children"),
    Output("fig", "children"),
    Input("selected_wafer", "children")
)
def updateChipFigures(wafer):
    con = load_most_recent()
    cdf = read_database(con, 'chips').execute()
    cdata = cdf.loc[cdf['Wafer_ID'] == wafer]

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
        fig.add_trace(go.Scatter(x=xC, y=yC, fill="toself", name=dff['Chip_ID']))

    figure = html.Div([dcc.Graph(figure=fig)])

    return dtable, figure


if __name__ == "__main__":
    app.run_server(jupyter_mode="external", port=8889, debug=True)
