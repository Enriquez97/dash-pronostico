import pandas as pd



def createTrain(df_partida,partida,porcentaje):
    df=df_partida.groupby(['al_periodo'])[[partida]].sum().reset_index()
    df['al_periodo']=df['al_periodo']+'01'
    df['al_periodo']=pd.to_datetime(df['al_periodo'])
    #df=df_partida[[partida]]
    #
    size_df=len(df)
    len_train=int(size_df*porcentaje)
    len_test=size_df-len_train
    #
    df_=df.set_index('al_periodo')
    df_.index.freq = 'MS'
    #
    train_data = df_[:len(df_)-len_test]

    test_data = df_[len(df_)-len_test:]

    return df_,train_data,test_data





"""
def createTrain(df_partida,partida):
    df=df_partida.groupby(['al_periodo'])[[partida]].sum().reset_index()
    df['al_periodo']=df['al_periodo']+'01'
    df['al_periodo']=pd.to_datetime(df['al_periodo'])
    #df=df_partida[[partida]]
    #
    size_df=len(df)
    len_train=int(size_df*0.95)
    len_test=size_df-len_train
    #
    df_=df.set_index('al_periodo')
    df_.index.freq = 'MS'
    #
    train_data = df_[:len(df_)-len_test]
    print(len(train_data))
    test_data = df_[len(df_)-len_test:]
    print(len(test_data))
    #test 
    test=test_data.copy()
    modelo_auto=auto_arima(train_data,start_p=0,d=1,start_q=0,
          max_p=4,max_d=2,max_q=4, start_P=0,
          D=1, start_Q=0, max_P=2,max_D=1,
          max_Q=2, m=12, seasonal=True,
          error_action='warn',trace=True,
          supress_warnings=True,stepwise=True,
          random_state=20,n_fits=50)
    #the best model
    num_m=str(modelo_auto)
    #print("-"+num_m[7]+"-"+num_m[9]+"-"+num_m[11]+"-"+num_m[14]+"-"+num_m[16]+"-"+num_m[18]+"-"+num_m[21:23])
    #CREATE ARIMA MODEL
    arima_model = SARIMAX(train_data[partida], order = (int(num_m[7]),int(num_m[9]),int(num_m[11])), seasonal_order = (int(num_m[14]),int(num_m[16]),int(num_m[18]),int(num_m[21:23]))).fit()
    # CREANDO DATA PREDECIDA
    arima_pred = arima_model.predict(start = len(train_data), end = len(df_)-1, typ="levels")
    arima_pred2 = arima_model.predict(start='2022-11-01',end='2024-01-01', typ="levels")#.rename("ARIMA Predictions")
    #test_data["ARIMA_Predictions"]=arima_pred
    
    df_predicted=pd.DataFrame(arima_pred2)
    
    return df_predicted
"""