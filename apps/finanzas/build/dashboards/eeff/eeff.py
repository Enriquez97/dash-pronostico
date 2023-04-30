from dash import Dash, dcc, html, Input, Output,State,dash_table,no_update
import pandas as pd
import dash_bootstrap_components as dbc
from django_plotly_dash import DjangoDash
import dash_mantine_components as dmc
from apps.finanzas.build.components.graphs.table import tableDMC,createTableDMC
from apps.finanzas.src.data.make_dataset import df_finanzas,all_partidas
from apps.finanzas.src.features.build_features import createTrimestre,separateItems
from apps.finanzas.src.models.train_model import createTrain
from apps.finanzas.src.models.predict_model import arima
from dash_iconify import DashIconify

from apps.finanzas.build.components.graphs.linechart import lineChart,scatterLine
from apps.finanzas.build.components.mantine_react_components.selects import select,multiSelect
from apps.finanzas.build.components.mantine_react_components.textbox import textInput
from apps.finanzas.build.components.mantine_react_components.loaders import loadingOverlay

data_finanzas=df_finanzas.copy()
external_stylesheets=[dbc.themes.BOOTSTRAP]

def partidasFinancieras():
    app = DjangoDash('dashboard_one', external_stylesheets=external_stylesheets)
    app.layout = html.Div([
        dmc.Title("Testear Pronóstico", align="center"),
        #dmc.Space(h=20),
          
        dbc.Row([
            dbc.Col([
                dmc.Card(
                        children=[
                            select('partida-input',texto='Partidas Financieras',place="",value=all_partidas[0],data=[{'label': i, 'value': i} for i in all_partidas]),
                            select('st-input',texto='Serie de Tiempo',place="",data=['Periodo Mensual','Periodo Trimestral'],value='Periodo Mensual'),
                            textInput(ids='fecha-first-pronostico',label='Inicio del Pronóstico',required=True,descripcion="Formato: YYYY-MM",value='2022-11'),
                            textInput(ids='fecha-last-pronostico',label='Fin del Pronóstico',required=True,descripcion="Formato: YYYY-MM",value='2023-12'),
                            select('tipo-moneda',texto='Moneda',place="",data=[{"value": "soles", "label": "PEN"},{"value": "dolares", "label": "USD"},],value='dolares'),
                            dmc.Text('Seleccine el porcentaje del dataset', weight=500,size="sm"),
                            dmc.Text('(Más bajo es más rápido. Más alto es más preciso)', weight=300,size="xs", color="gray"),
                            dcc.Slider(
                                    id="percet-dataset",
                                    min=1,
                                    max=100,
                                    step=1,
                                    marks={
                                        0: "0%",
                                        10: "",
                                        20: "20%",
                                        30: "",
                                        40: "40%",
                                        50: "",
                                        60: "60%",
                                        70: "",
                                        80: "80%",
                                        90: "",
                                        100: "100%",
                                    },
                                    value=90,
                                ),
                            
                            ],
                        withBorder=True,
                        shadow="sm",
                        radius="md",
                        
                    )
            ] ,width=3,className="col-xl-3 col-md-3 col-sm-12 col-12 mb-3"),
            dbc.Col([
                dmc.Tabs(
                    [
                        dmc.TabsList(
                            [
                                dmc.Tab(
                                    "Serie de Tiempo",
                                    icon=DashIconify(icon="tabler:chart-line"),
                                    value="st",
                                ),
                                dmc.Tab(
                                    "Data",
                                    icon=DashIconify(icon="tabler:table"),
                                    value="data",
                                ),
                                dmc.Tab(
                                    "Data de Entrenamiento",
                                    icon=DashIconify(icon="tabler:database"),
                                    value="data-train",
                                ),
                            ]
                        ),
                        dmc.TabsPanel(loadingOverlay(dbc.Card(dcc.Graph(id='graph-partida-pronostico'),className="shadow-sm")), value='st'),
                        dmc.TabsPanel(html.Div(id='table-data',style={'max-height': '400px','overflow': "auto"}), value='data'),
                        dmc.TabsPanel(html.Div(id='table-data-train',style={'max-height': '400px','overflow': "auto"}), value='data-train'),
                    ],
                    value="st",
                ),
                
            ],width=9,className="col-xl-9 col-md-9 col-sm-12 col-12 mb-3"),
        #
        ]),

    ])#,style={'backgroundColor':'white'}

     
    
    @app.callback(
            Output('graph-partida-pronostico','figure'),
            Output('table-data','children'),
            Output('table-data-train','children'),
            Input('partida-input','value'),
            Input('st-input','value'),
            Input('tipo-moneda','value'),
            Input('fecha-first-pronostico','value'),
            Input('fecha-last-pronostico','value'),
            Input('percet-dataset','value')

    )
    def update(partida,serie_time,moneda,fecha_first,fecha_last,percent):
        inicio=fecha_first+'-01'
        fin=fecha_last+'-01'
        porcentaje=int(percent)/100
        #start_date='2022-11-01'
        us_df=separateItems(data_finanzas,ejex=serie_time,tipo_moneda=moneda)
        us_df=us_df.rename(columns={'PATRIMONIO_x':'PATRIMONIO'})
        data_train_test=createTrain(us_df,partida,porcentaje)
        df=data_train_test[0]
        #periodo de inicio del pronostico
        inicio_pronostico=str(df.index.unique()[-1])
        
        train_data=data_train_test[1]
        test_data=data_train_test[2]
        ###CAMBIAR EL PRIMER ELEMENTO DE LA PREDICCION
        #dato_last=df[partida][inicio]
        print(df.columns)
        df_predicted=arima(df,train_data,partida,inicio,fin)
        print(df_predicted.columns)
        title=f"{partida} - {percent}% dataset ({moneda})"
        #df_predicted['predicted_mean'][inicio]=dato_last
        return scatterLine(title,df,df_predicted,partida,partida,moneda,inicio_pronostico,fin,inicio),tableDMC(createTableDMC(df.reset_index())),tableDMC(createTableDMC(df_predicted.reset_index()))



    

def creandoTablaPronostico(moneda='dolares'):
    inicio='2022-11-01'
    fin='2024-01-01'
    porcentaje=0.95
    serie_time='Periodo Mensual'
    #convirtiendo partidas a columnas
    df=separateItems(data_finanzas,ejex=serie_time,tipo_moneda=moneda)
    df=df.rename(columns={'PATRIMONIO_x':'PATRIMONIO'})
    df_table_predict=pd.DataFrame()
    #test_partidas=['ACTIVO','PASIVO','PATRIMONIO']
    for columns in all_partidas:#all_partidas[-3:]:
        if df[columns].unique()[0]!=0 or df[columns].unique()[-1]!=0:
            data_train_test=createTrain(df,columns,porcentaje)
            df_data_train_test=data_train_test[0]
            train_data=data_train_test[1]
            test_data=data_train_test[2]
            df_predicted=arima(df_data_train_test,train_data,columns,inicio,fin)
            #nuevo data frame general
            #df_table_predict['al_periodo']=df_predicted.index
            df_table_predict[columns]=df_predicted[columns]
            print(df_table_predict.columns)
        ########################
        else:
            df_table_predict[columns]=0
    return df_table_predict
#print(creandoTablaPronostico)
#creandoTablaPronostico(moneda='dolares').to_excel('pronostico_partidas_dolares.xlsx')
#creandoTablaPronostico(moneda='soles').to_excel('pronostico_partidas_soles.xlsx')
#df_pronostico=pd.read_excel('pronostico_partidas_dolares.xlsx')
#print(df_pronostico)


