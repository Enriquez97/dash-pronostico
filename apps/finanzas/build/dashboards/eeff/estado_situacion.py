from dash import Dash, dcc, html, Input, Output,State,dash_table,no_update
import pandas as pd
import dash_bootstrap_components as dbc
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
from apps.finanzas.build.components.graphs.table import tableDMC,createTableDMC,createRowTable,tableSimpleDMC
from apps.finanzas.src.data.make_dataset import df_finanzas,all_partidas,all_periodo
from apps.finanzas.src.features.build_features import createTrimestre,separateItems,dataframeBalanceAPP,dataframeTestPronostico
from apps.finanzas.src.models.train_model import createTrain
from apps.finanzas.src.models.predict_model import arima
from dash_iconify import DashIconify
from apps.finanzas.build.components.graphs.linechart import lineChart,scatterLine
from apps.finanzas.build.components.graphs.treemap import treemapEstadoSituacion
from apps.finanzas.build.components.mantine_react_components.selects import select,multiSelect
from apps.finanzas.build.components.mantine_react_components.textbox import textInput
from apps.finanzas.build.components.mantine_react_components.loaders import loadingOverlay
from apps.finanzas.build.components.mantine_react_components.actionIcon import btnFilter,btnCollapse


external_stylesheets=[dbc.themes.BOOTSTRAP]
data_finanzas=df_finanzas.copy()
#modelo 3table
def table_dash(dataframe):
       return dash_table.DataTable(
        data=dataframe.to_dict('records'),
        columns=[
            {'name': i, 'id': i}
            if i != 'Date' else
            {'name': 'Date', 'id': 'Date', 'type': 'datetime'}
            for i in dataframe.columns
        ],
        style_table={'overflowY': 'auto'},
        fixed_rows={'headers': True},
        style_as_list_view=True,
                    style_cell={'padding': '12px',
                                 'font-family': 'sans-serif',
                                  'font-size': '14px',
                                  'text_align': 'left',
                                  #'minWidth': 30, 'maxWidth': 70, #'width': 95
                                },
                    style_header={
                        'backgroundColor': 'white',
                        'fontWeight': 'bold',
                        'text_align': 'left',
                        'font-size': '14px',
                    },
        style_data_conditional=[
        {
            'if': {
                'filter_query': '{ACTIVO CORRIENTE} contains "Total"'
            },
            'backgroundColor': '#0074D9',
            'color': 'white',
            'fontWeight': 'bold',
        }
    ]
        
    )



def dashEstadoSituacion():
    app = DjangoDash('estado_situacion', external_stylesheets=external_stylesheets)
    app.layout = html.Div([
        dbc.Row([
            dbc.Col([
                btnCollapse()
            ],width=1,className="col-xl-1 col-md-1 col-sm-1 col-1 mb-3"),
            dbc.Col([
                dmc.Title("Estado de Situción Financiera", align="center",order=3,color="blue"),
                dmc.Title(id='subtitle-periodo', align="center",order=4,color="blue"),
                dmc.Title(id='subtitle-moneda', align="center",order=6,color="blue"),
            ],width=7,className="col-xl-7 col-md-7 col-sm-11 col-11 mb-3"),
            dbc.Col([
                select('periodo-input',texto='Periodos',place="",value=all_periodo[-1],data=[{'label': i, 'value': i} for i in all_periodo]),
            ],width=2,className="col-xl-2 col-md-2 col-sm-12 col-12 mb-3"),
            dbc.Col([
                select('tipo-moneda',texto='Moneda',place="",data=[{"value": "soles", "label": "PEN"},{"value": "dolares", "label": "USD"},],value='dolares'),
            ],width=2,className="col-xl-2 col-md-2 col-sm-12 col-12 mb-3"),
        ]),
        dbc.Collapse(
            dbc.Row([
                dbc.Col([
                    html.Div(id='card-estado-situacion-financiera'),
        
                    
                ],width=12,className="col-xl-12 col-md-12 col-sm-12 col-12 mb-3"),
            ]),
        id="collapse",is_open=True),
            dbc.Row([
                dbc.Col([
                    loadingOverlay(dbc.Card(dcc.Graph(id='figure-treemap-sf'),className="shadow-sm"))
                ],width=12,className="col-xl-12 col-md-12 col-sm-12 col-12 mb-3"),
            ]),
        
    ])
    @app.callback(
        Output("collapse", "is_open"),
        [Input("btn-collapse", "n_clicks")],
        [State("collapse", "is_open")],
        )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open
    
    @app.callback(
        Output("subtitle-periodo", "children"),
        Output("subtitle-moneda", "children"),
        [
         Input("periodo-input", "value"),
         Input("tipo-moneda", "value")
        ],

        )
    def update_subtitles(periodo, moneda):
        df=data_finanzas[data_finanzas['al_periodo']==periodo]
        moth_text=df['Mes'].unique()[0]
        year=df['Año'].unique()[0]
        text_subtitle_periodo=f'{moth_text} del {year}'
        text_subtitle_moneda=f'Expresado en {moneda}'
        return text_subtitle_periodo,text_subtitle_moneda


    @app.callback(
        Output("card-estado-situacion-financiera", "children"),
        Output("figure-treemap-sf", "figure"),
        [
         Input("periodo-input", "value"),
         Input("tipo-moneda", "value")
        ],

        )
    def update_situacion_financiera(periodo,moneda):
        if moneda == 'soles':
            value_moneda='saldo_cargo_mof'
        elif moneda == 'dolares':
            value_moneda='saldo_cargo_mex'    
        df=data_finanzas[data_finanzas['al_periodo']==periodo]
        df_bc=df.groupby(['grupo1','grupo2','grupo3'])[[value_moneda]].sum().reset_index()
        #totales filtrados
        total_activo="{:,.2f}".format(df_bc[df_bc['grupo1']=='ACTIVO'][value_moneda].sum())
        total_pasivo=df_bc[df_bc['grupo1']=='PASIVO'][value_moneda].sum()
        total_patrimonio=df_bc[df_bc['grupo1']=='PATRIMONIO'][value_moneda].sum()
        total_pasivo_patri="{:,.2f}".format(total_pasivo+total_patrimonio)

        card_estado_situacion=html.Div([
                                    dmc.Card(
                                                    children=[
                                                        dbc.Row([
                                                            dbc.Col([
                                                                dmc.Text("ACTIVO", size="md", weight=600),
                                                                #dmc.Text("ACTIVO CORRIENTE", size="sm"),html.Div(),html.Div(),
                                                                tableSimpleDMC(createTableDMC(dataframeBalanceAPP(df_bc,partida_grupo_1='ACTIVO',importe=value_moneda,partida_grupo_2='ACTIVO CORRIENTE',label_total='Total Activo Corriente'))),
                                                                tableSimpleDMC(createTableDMC(dataframeBalanceAPP(df_bc,partida_grupo_1='ACTIVO',importe=value_moneda,partida_grupo_2='ACTIVO NO CORRIENTE',label_total='Total Activo no Corriente'))),
                                                                dmc.Space(h=20),
                                                                dmc.Grid(
                                                                            children=[
                                                                                dmc.Col(dmc.Text("TOTAL ACTIVO", size="md", weight=600), span=4),
                                                                                dmc.Col(html.Div(""), span=5),
                                                                                dmc.Col(dmc.Text(children=[total_activo], size="md", weight=600), span=3),
                                                                            ],
                                                                            gutter="xl",
                                                                        ),
                                                                
                                                            ],width=6,className="col-xl-6 col-md-6 col-sm-12 col-12 mb-3"),
                                                            dbc.Col([
                                                                dmc.Text("PASIVO", size="md", weight=600),
                                                                tableSimpleDMC(createTableDMC(dataframeBalanceAPP(df_bc,partida_grupo_1='PASIVO',importe=value_moneda,partida_grupo_2='PASIVO CORRIENTE',label_total='Total Pasivo Corriente'))),
                                                                tableSimpleDMC(createTableDMC(dataframeBalanceAPP(df_bc,partida_grupo_1='PASIVO',importe=value_moneda,partida_grupo_2='PASIVO NO CORRIENTE',label_total='Total Pasivo no Corriente'))),
                                                                tableSimpleDMC(createTableDMC(dataframeBalanceAPP(df_bc,partida_grupo_1='PATRIMONIO',importe=value_moneda,partida_grupo_2='PATRIMONIO',label_total='Total Patrimonio'))),
                                                                dmc.Grid(
                                                                            children=[
                                                                                dmc.Col(dmc.Text("TOTAL PASIVO y PATRIMONIO", size="md", weight=600), span=4),
                                                                                dmc.Col(html.Div(""), span=5),
                                                                                dmc.Col(dmc.Text(children=[total_pasivo_patri], size="md", weight=600), span=3),
                                                                            ],
                                                                            gutter="xl",
                                                                        ),
                                                                
                                                            ],width=6,className="col-xl-6 col-md-6 col-sm-12 col-12 mb-3"),
                                                        ]),
                                                    ],
                                                    withBorder=True,
                                                    shadow="sm",
                                                    radius="md",
                                                    
                                                )
                                ])
        treemap_graph=treemapEstadoSituacion(df_bc,moneda=value_moneda,titulo='Partidas Financieras Treemap',list_path=['grupo1', 'grupo2', 'grupo3'])
        return card_estado_situacion,treemap_graph

def dashEstadoSituacionPronostico():
    app = DjangoDash('estado_situacion', external_stylesheets=external_stylesheets)
    app.layout = html.Div([
        dbc.Row([
            dbc.Col([
                btnCollapse()
            ],width=1,className="col-xl-1 col-md-1 col-sm-1 col-1 mb-3"),
            dbc.Col([
                dmc.Title("Estado de Situción Financiera", align="center",order=3,color="blue"),
                dmc.Title(id='subtitle-periodo', align="center",order=4,color="blue"),
                dmc.Title(id='subtitle-moneda', align="center",order=6,color="blue"),
            ],width=7,className="col-xl-7 col-md-7 col-sm-11 col-11 mb-3"),
            dbc.Col([
                select('periodo-input',texto='Periodos',place="",value=all_periodo[-1],data=[{'label': i, 'value': i} for i in all_periodo]),
            ],width=2,className="col-xl-2 col-md-2 col-sm-12 col-12 mb-3"),
            dbc.Col([
                select('tipo-moneda',texto='Moneda',place="",data=[{"value": "soles", "label": "PEN"},{"value": "dolares", "label": "USD"},],value='dolares'),
            ],width=2,className="col-xl-2 col-md-2 col-sm-12 col-12 mb-3"),
        ]),
        dbc.Collapse(
            dbc.Row([
                dbc.Col([
                    html.Div(id='card-estado-situacion-financiera'),
        
                    
                ],width=12,className="col-xl-12 col-md-12 col-sm-12 col-12 mb-3"),
            ]),
        id="collapse",is_open=True),
            dbc.Row([
                dbc.Col([
                    loadingOverlay(dbc.Card(dcc.Graph(id='figure-treemap-sf'),className="shadow-sm"))
                ],width=12,className="col-xl-12 col-md-12 col-sm-12 col-12 mb-3"),
            ]),
        
    ])
    @app.callback(
        Output("collapse", "is_open"),
        [Input("btn-collapse", "n_clicks")],
        [State("collapse", "is_open")],
        )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open
    
    @app.callback(
        Output("subtitle-periodo", "children"),
        Output("subtitle-moneda", "children"),
        [
         Input("periodo-input", "value"),
         Input("tipo-moneda", "value")
        ],

        )
    def update_subtitles(periodo, moneda):
        df=data_finanzas[data_finanzas['al_periodo']==periodo]
        moth_text=df['Mes'].unique()[0]
        year=df['Año'].unique()[0]
        text_subtitle_periodo=f'{moth_text} del {year}'
        text_subtitle_moneda=f'Expresado en {moneda}'
        return text_subtitle_periodo,text_subtitle_moneda


    @app.callback(
        Output("card-estado-situacion-financiera", "children"),
        Output("figure-treemap-sf", "figure"),
        [
         Input("periodo-input", "value"),
         Input("tipo-moneda", "value")
        ],

        )
    def update_situacion_financiera(periodo,moneda):
        if moneda == 'soles':
            value_moneda='saldo_cargo_mof'
        elif moneda == 'dolares':
            value_moneda='saldo_cargo_mex'    
        df=data_finanzas[data_finanzas['al_periodo']==periodo]
        df_bc=df.groupby(['grupo1','grupo2','grupo3'])[[value_moneda]].sum().reset_index()
        #totales filtrados
        total_activo="{:,.2f}".format(df_bc[df_bc['grupo1']=='ACTIVO'][value_moneda].sum())
        total_pasivo=df_bc[df_bc['grupo1']=='PASIVO'][value_moneda].sum()
        total_patrimonio=df_bc[df_bc['grupo1']=='PATRIMONIO'][value_moneda].sum()
        total_pasivo_patri="{:,.2f}".format(total_pasivo+total_patrimonio)

        card_estado_situacion=html.Div([
                                    dmc.Card(
                                                    children=[
                                                        dbc.Row([
                                                            dbc.Col([
                                                                dmc.Text("ACTIVO", size="md", weight=600),
                                                                #dmc.Text("ACTIVO CORRIENTE", size="sm"),html.Div(),html.Div(),
                                                                #table_dash
                                                                #tableSimpleDMC(createTableDMC(dataframeTestPronostico(df_bc,partida_grupo_1='ACTIVO',importe=value_moneda,partida_grupo_2='ACTIVO CORRIENTE',label_total='Total Activo Corriente'))),
                                                                tableSimpleDMC(table_dash(dataframeBalanceAPP(df_bc,partida_grupo_1='ACTIVO',importe=value_moneda,partida_grupo_2='ACTIVO CORRIENTE',label_total='Total Activo Corriente'))),
                                                                tableSimpleDMC(createTableDMC(dataframeBalanceAPP(df_bc,partida_grupo_1='ACTIVO',importe=value_moneda,partida_grupo_2='ACTIVO NO CORRIENTE',label_total='Total Activo no Corriente'))),
                                                                dmc.Space(h=20),
                                                                dmc.Grid(
                                                                            children=[
                                                                                dmc.Col(dmc.Text("TOTAL ACTIVO", size="md", weight=600), span=4),
                                                                                dmc.Col(html.Div(""), span=5),
                                                                                dmc.Col(dmc.Text(children=[total_activo], size="md", weight=600), span=3),
                                                                            ],
                                                                            gutter="xl",
                                                                        ),
                                                                dmc.Text("PASIVO", size="md", weight=600),
                                                                tableSimpleDMC(createTableDMC(dataframeBalanceAPP(df_bc,partida_grupo_1='PASIVO',importe=value_moneda,partida_grupo_2='PASIVO CORRIENTE',label_total='Total Pasivo Corriente'))),
                                                                tableSimpleDMC(createTableDMC(dataframeBalanceAPP(df_bc,partida_grupo_1='PASIVO',importe=value_moneda,partida_grupo_2='PASIVO NO CORRIENTE',label_total='Total Pasivo no Corriente'))),
                                                                tableSimpleDMC(createTableDMC(dataframeBalanceAPP(df_bc,partida_grupo_1='PATRIMONIO',importe=value_moneda,partida_grupo_2='PATRIMONIO',label_total='Total Patrimonio'))),
                                                                dmc.Grid(
                                                                            children=[
                                                                                dmc.Col(dmc.Text("TOTAL PASIVO y PATRIMONIO", size="md", weight=600), span=4),
                                                                                dmc.Col(html.Div(""), span=5),
                                                                                dmc.Col(dmc.Text(children=[total_pasivo_patri], size="md", weight=600), span=3),
                                                                            ],
                                                                            gutter="xl",
                                                                        ),
                                                                
                                                            ],width=6,className="col-xl-12 col-md-12 col-sm-12 col-12 mb-3"),
                                                            
                                                        ]),
                                                    ],
                                                    withBorder=True,
                                                    shadow="sm",
                                                    radius="md",
                                                    
                                                )
                                ])
        treemap_graph=treemapEstadoSituacion(df_bc,moneda=value_moneda,titulo='Partidas Financieras Treemap',list_path=['grupo1', 'grupo2', 'grupo3'])
        return card_estado_situacion,treemap_graph
#df=data_finanzas[data_finanzas['al_periodo']=='202001']
#df_bc=df.groupby(['grupo1','grupo2','grupo3'])[['saldo_cargo_mex']].sum().reset_index()   
#print(dataframeBalanceAPP(df_bc,partida_grupo_1='PASIVO',importe='saldo_cargo_mex',partida_grupo_2='PASIVO CORRIENTE',label_total='Total Pasivo Corriente'))
#print(dataframeTestPronostico(df_bc,partida_grupo_1='PASIVO',importe='saldo_cargo_mex',partida_grupo_2='PASIVO CORRIENTE',label_total='Total Pasivo Corriente'))