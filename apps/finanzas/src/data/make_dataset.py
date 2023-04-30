import pandas as pd
import numpy as np
import DateTime as dt
from datetime import datetime, timedelta
from apps.finanzas.src.features.build_features import *
from apps.finanzas.src.data.credentials import TOKEN,API
from apps.finanzas.src.models.train_model import createTrain

finanzas=getApi(API,TOKEN)
df=pd.DataFrame(finanzas)

#df = pd.read_json("http://68.168.108.184:3000/api/consulta/nsp_eeff_json/")

#print(df_finanzas)
df_finanzas=createTrimestre(df)
#print(df_finanzas)
#print(df_finanzas.columns)

all_partidas=list(df_finanzas['grupo1'].dropna().unique())+list(df_finanzas['grupo2'].dropna().unique())+list(df_finanzas['grupo3'].dropna().unique())+list(df_finanzas['grupo_funcion'].dropna().unique())
all_periodo=df_finanzas['al_periodo'].unique()
#df_finanzas_periodo_d=separateItems(df_finanzas)


#df_train=createTrain(df_finanzas_periodo_d,'Clientes')
#print(df_train)



