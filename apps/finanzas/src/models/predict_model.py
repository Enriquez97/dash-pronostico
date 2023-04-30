import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.graphics.tsaplots import plot_acf,plot_pacf 
from statsmodels.tsa.seasonal import seasonal_decompose 
from statsmodels.tsa.stattools import adfuller
# Métrica de Evaluación
from sklearn.metrics import mean_squared_error
from statsmodels.tools.eval_measures import rmse
from sklearn import metrics
from pmdarima import auto_arima   
from sklearn.preprocessing import MinMaxScaler
from keras.preprocessing.sequence import TimeseriesGenerator
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM


def arima(df_,train_data,partida,fecha_inicio,fecha_final):
    
    modelo_auto=auto_arima(train_data,start_p=0,d=1,start_q=0,
          max_p=4,max_d=2,max_q=4, start_P=0,
          D=1, start_Q=0, max_P=2,max_D=1,
          max_Q=2, m=12, seasonal=True,
          error_action='warn',trace=True,
          supress_warnings=True,stepwise=True,
          random_state=20,n_fits=50)
    #the best model
    num_m=str(modelo_auto)
    #CREATE ARIMA MODEL
    arima_model = SARIMAX(train_data[partida], order = (int(num_m[7]),int(num_m[9]),int(num_m[11])), seasonal_order = (int(num_m[14]),int(num_m[16]),int(num_m[18]),int(num_m[21:23]))).fit()
    # CREANDO DATA PREDECIDA
    #arima_pred = arima_model.predict(start = len(train_data), end = len(df_)-1, typ="levels")
    arima_pred2 = arima_model.predict(start=fecha_inicio,end=fecha_final, typ="levels").rename(partida)
    #test_data["ARIMA_Predictions"]=arima_pred
    df_predicted=pd.DataFrame(arima_pred2)
    return df_predicted

def lstmForecast(df_,train_data,test_data,partida):
    scaler = MinMaxScaler()
    scaler.fit(train_data)
    scaled_train_data = scaler.transform(train_data)
    scaled_test_data = scaler.transform(test_data)
    shape_scaled_test_data=str(scaled_test_data.shape)

    n_input = int(shape_scaled_test_data[1])
    n_features= int(shape_scaled_test_data[4])
    generator = TimeseriesGenerator(scaled_train_data, scaled_train_data, length=n_input, batch_size=1)
    lstm_model = Sequential()
    lstm_model.add(LSTM(200, activation='relu', input_shape=(n_input, n_features)))#capa de 200
    lstm_model.add(Dense(1))
    lstm_model.compile(optimizer='adam', loss='mse')
    lstm_model.fit_generator(generator,epochs=100)
    lstm_predictions_scaled = list()
    batch = scaled_train_data[-n_input:]
    current_batch = batch.reshape((1, n_input, n_features))

    for i in range(len(test_data)):   
        lstm_pred = lstm_model.predict(current_batch)[0]
        lstm_predictions_scaled.append(lstm_pred) 
        current_batch = np.append(current_batch[:,1:,:],[[lstm_pred]],axis=1)
    lstm_predictions = scaler.inverse_transform(lstm_predictions_scaled)
    lstm_predictions = scaler.inverse_transform(lstm_predictions_scaled)

    return lstm_predictions
