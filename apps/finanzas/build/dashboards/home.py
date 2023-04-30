from dash import Dash, dcc, html, Input, Output,State,dash_table,no_update
from dash.dash_table.Format import Format, Group, Scheme, Symbol
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import dash_bootstrap_components as dbc
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
import dash_ag_grid as dag     

external_stylesheets=[dbc.themes.BOOTSTRAP]
data = px.data.stocks()

def Home():
    app = DjangoDash('home', external_stylesheets=external_stylesheets)
    
    app.layout = html.Div(
    
    children=[
        dmc.Title(
            "Equity prices - Line chart and Table data", align="center"),
        dmc.Space(h=20),
        dmc.Button("Download Table Data", id="btn_csv"),
        dcc.Download(id="download-dataframe-csv"),
        dmc.Space(h=10),
        dmc.MultiSelect(
            label="Select stock you like!",
            placeholder="Select all stocks you like!",
            id="stock-dropdown",
            value=["GOOG", "AAPL"],
            data=[{"label": i, "value": i} for i in data.columns[1:]],
        ),
        dmc.Space(h=60),
        dmc.SimpleGrid(
            [
                dcc.Graph(id="line_chart"),
                dash_table.DataTable(
                    data.to_dict("records"),
                    [{"name": i, "id": i} for i in data.columns],
                    page_size=10,
                    style_table={"overflow-x": "auto"},
                ),
            ],
            cols=2,
            id="simple_grid_layout",
            breakpoints=[
                {"maxWidth": 1500, "cols": 2, "spacing": "md"},
                {
                    "maxWidth": 992,
                    "cols": 1,
                    "spacing": "sm",
                },  # common screen size for small laptops
                {
                    "maxWidth": 768,
                    "cols": 1,
                    "spacing": "sm",
                },  # common screen size for tablets
            ],
        ),
    ],
)



    @app.callback(
        Output("line_chart", "figure"),
        Input("stock-dropdown", "value"),
    )
    def select_stocks(stocks):
        fig = px.line(data_frame=data, x="date", y=stocks, template="simple_white")
        fig.update_layout(
            margin=dict(t=50, l=25, r=25, b=25), yaxis_title="Price", xaxis_title="Date"
        )
        return fig


    @app.callback(
        Output("download-dataframe-csv", "data"),
        Input("btn_csv", "n_clicks"),
        prevent_initial_call=True,
    )
    def func(n_clicks):
        return dcc.send_data_frame(data.to_csv, "mydf.csv")
    
def Home2():
    app = DjangoDash('home', external_stylesheets=external_stylesheets)
    df = pd.read_csv("https://raw.githubusercontent.com/Coding-with-Adam/Dash-by-Plotly/master/Ag-Grid/row-deletion/finance_survey.csv")
    df['Invest'] = 'sell'

    columnDefs = [
        {
            "headerName": "Gender",  # Name of table displayed in app
            "field": "Gender",       # ID of table (needs to be the same as excel sheet column name)
            "checkboxSelection": True,
        },
        {
            "headerName": "Age",
            "field": "Age",
            "type": "rightAligned",
            "filter": "agNumberColumnFilter",
        },
        {
            "headerName": "Money",
            "field": "Money",
            "type": "rightAligned",
            "filter": "agNumberColumnFilter",
        },
        {
            "headerName": "Stock_Market",
            "field": "Stock_Market",
        },
        {
            "headerName": "Objective",
            "field": "Objective",
        },
        {
            "headerName": "Source",
            "field": "Source",
        },
        {
            "headerName": "Invest",
            "field": "Invest",
            "cellRenderer": "Button",
            "cellRendererParams": {"className": "btn btn-info"},
        },
    ]

    defaultColDef = {
        "filter": True,
        "floatingFilter": True,
        "resizable": True,
        "sortable": True,
        "editable": True,
        "minWidth": 125,
    }



    table = dag.AgGrid(
        id="portfolio-table",
        className="ag-theme-alpine-dark",
        columnDefs=columnDefs,
        rowData=df.to_dict('records'),
        columnSize="sizeToFit",
        defaultColDef=defaultColDef,
        dashGridOptions={"undoRedoCellEditing": True, "rowSelection":"multiple"},
    )


    app.layout = dbc.Container(
        [
            html.Div("Investments Survey", className="h3 p-2 text-white bg-secondary"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            table,
                                        ]
                                    ),
                                ],
                            )
                        ], width={"size": 10, "offset": 1},
                    ),
                ],
                className="py-4",
            ),
        ],
    )

    @app.callback(
        Output("portfolio-table", "rowData"),
        Input("portfolio-table", "cellRendererData"),
    )
    def showChange(n):
        if n:
            print(n)
            row_id_sold = int(n['rowId'])
            patched_table = Patch()
            patched_table[row_id_sold]['Money'] = 0
            return patched_table
        else:
            return no_update

