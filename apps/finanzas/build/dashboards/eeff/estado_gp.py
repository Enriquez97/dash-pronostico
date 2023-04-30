from dash import Dash, dcc, html, Input, Output,State,dash_table,no_update
import pandas as pd
import dash_bootstrap_components as dbc
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
from apps.finanzas.build.components.graphs.table import tableDMC,createTableDMC,createRowTable,tableSimpleDMC
from apps.finanzas.src.data.make_dataset import df_finanzas,all_partidas,all_periodo
from apps.finanzas.src.features.build_features import createTrimestre,separateItems,dataframeBalanceAPP
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
data_finanzas['month']=data_finanzas['month'].astype("int")


def dashEstadoGananciasPerdidas():
    app = DjangoDash('estado_gp', external_stylesheets=external_stylesheets)
    app.layout = html.Div([
        dbc.Row([
            dbc.Col([
                btnCollapse()
            ],width=1,className="col-xl-1 col-md-1 col-sm-1 col-1 mb-3"),
            dbc.Col([
                dmc.Title("Estado de Ganancias y Pérdidas por Función", align="center",order=3,color="blue"),
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
                    html.Div(id='card-estado-gp-funcion'),
                ],width=12,className="col-xl-12 col-md-12 col-sm-12 col-12 mb-3"),
            ]),
        id="collapse",is_open=True),

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
        year=periodo[:4]
        month=int(periodo[4:])
        
        df=data_finanzas[(data_finanzas['Año']==year)&(data_finanzas['month']>=1)&(data_finanzas['month']<=month)]
        
        month_inicio=df['Mes'].unique()[0]
        month_fin=df['Mes'].unique()[-1]
        year_text=df['Año'].unique()[0]
        text_subtitle_periodo=f'Desde {month_inicio}{year_text} Hasta {month_fin}{year_text}'
        text_subtitle_moneda=f'Expresado en {moneda}'
        return text_subtitle_periodo,text_subtitle_moneda
    
    @app.callback(
        Output("card-estado-gp-funcion", "children"),
        [
         Input("periodo-input", "value"),
         Input("tipo-moneda", "value")
        ],

        )
    def update_tabla_gp(periodo, moneda):
        if moneda == 'soles':
            value_moneda='saldo_cargo_mof'
        elif moneda == 'dolares':
            value_moneda='saldo_cargo_mex'   
        year=periodo[:4]
        month=int(periodo[4:])
        df=data_finanzas[(data_finanzas['Año']==year)&(data_finanzas['month']>=1)&(data_finanzas['month']<=month)]
        df_pg=df.groupby(['grupo_funcion','Año','Mes','al_periodo'])[[value_moneda]].sum().reset_index()
        #df_pg[value_moneda] = df_pg.apply(lambda x: "{:,.2f}".format(x[value_moneda]), axis=1)    
        df_pg_pivot=df_pg.pivot_table(index=('grupo_funcion'),values='saldo_cargo_mex',columns='al_periodo').reset_index()
        # listas de las partidas
        UTILIDAD_BRUTA=['VENTAS DE MERCADERIAS','COSTO DE VENTAS DE MERCADERIAS','COSTO DE PRODUCTOS MANUFACTURADOS','COSTO DEL SERVICIO']
        UTILIDAD_OPERATIVA=['GASTOS DE VENTAS','GASTOS ADMINISTRATIVOS','OTROS INGRESOS','GASTOS NO DEDUCIBLES']
        UTILIDAD_ANTES_DEL_IMPUESTO_RENTA=['GASTOS FINANCIEROS','INGRESOS FINANCIEROS','GANANCIA POR DIFERENCIA DE CAMBIO','PERDIDA POR DIFERENCIA DE CAMBIO']
        #dataframe para tabla utilidad bruta
        df_utilidad_bruta=df_pg_pivot[df_pg_pivot['grupo_funcion'].isin(UTILIDAD_BRUTA)]
        df_utilidad_bruta.loc['TOTAL',:]= df_utilidad_bruta.sum(numeric_only=True, axis=0)  
        df_utilidad_bruta.loc[:,'TOTAL']= df_utilidad_bruta.sum(numeric_only=True, axis=1)
        df_utilidad_bruta=df_utilidad_bruta.fillna('Utilidad Bruta')
        for periodo_col in df_utilidad_bruta.columns[1:]:
            df_utilidad_bruta[periodo_col] = df_utilidad_bruta.apply(lambda x: "{:,.2f}".format(x[periodo_col]), axis=1)     
        #dataframe para tabla utilidad operativa
        df_utilidad_operativa=df_pg_pivot[df_pg_pivot['grupo_funcion'].isin(UTILIDAD_OPERATIVA)]
        df_utilidad_operativa.loc['TOTAL',:]= df_utilidad_operativa.sum(numeric_only=True, axis=0)  
        df_utilidad_operativa.loc[:,'TOTAL']= df_utilidad_operativa.sum(numeric_only=True, axis=1)
        df_utilidad_operativa=df_utilidad_operativa.fillna('EBIT')
        for periodo_col in df_utilidad_operativa.columns[1:]:
            df_utilidad_operativa[periodo_col] = df_utilidad_operativa.apply(lambda x: "{:,.2f}".format(x[periodo_col]), axis=1)    
        #df_utilidad_operativa[value_moneda] = df_utilidad_operativa.apply(lambda x: "{:,.2f}".format(x[value_moneda]), axis=1)

        #dataframe para tabla utilidad impuesto renta
        df_utilidad_impuesto_renta=df_pg_pivot[df_pg_pivot['grupo_funcion'].isin(UTILIDAD_ANTES_DEL_IMPUESTO_RENTA)]
        df_utilidad_impuesto_renta.loc['TOTAL',:]= df_utilidad_impuesto_renta.sum(numeric_only=True, axis=0)  
        df_utilidad_impuesto_renta.loc[:,'TOTAL']= df_utilidad_impuesto_renta.sum(numeric_only=True, axis=1)
        df_utilidad_impuesto_renta=df_utilidad_impuesto_renta.fillna('EBT')
        for periodo_col in df_utilidad_impuesto_renta.columns[1:]:
            df_utilidad_impuesto_renta[periodo_col] = df_utilidad_impuesto_renta.apply(lambda x: "{:,.2f}".format(x[periodo_col]), axis=1)
        card_estado_gp=html.Div([
                                    dmc.Card(
                                                    children=[
                                                        dbc.Row([
                                                            dbc.Col([
                                                                #dmc.Text("ACTIVO", size="md", weight=600),
                                                                #dmc.Text("ACTIVO CORRIENTE", size="sm"),html.Div(),html.Div(),
                                                                tableSimpleDMC(createTableDMC(df_utilidad_bruta)),
                                                                tableSimpleDMC(createTableDMC(df_utilidad_operativa)),
                                                                tableSimpleDMC(createTableDMC(df_utilidad_impuesto_renta)),
                                                                #dmc.Space(h=20),
                                                                #dmc.Grid(
                                                                #            children=[
                                                                #                dmc.Col(dmc.Text("TOTAL ACTIVO", size="md", weight=600), span=4),
                                                                #                dmc.Col(html.Div(""), span=5),
                                                                #                dmc.Col(dmc.Text(children=[total_activo], size="md", weight=600), span=3),
                                                                #            ],
                                                                #            gutter="xl",
                                                                #        ),
                                                                
                                                            ],width=12,className="col-xl-12 col-md-12 col-sm-12 col-12 mb-3"),
                                                        ])
                                                    ],
                                                    withBorder=True,
                                                    shadow="sm",
                                                    radius="md",
                                                    
                                                )
                                ])
        return card_estado_gp