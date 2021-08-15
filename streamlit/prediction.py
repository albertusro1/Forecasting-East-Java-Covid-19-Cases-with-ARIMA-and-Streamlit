import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima_model import ARIMA
from sklearn import metrics
import json
import datetime
import requests
import warnings
from matplotlib.pylab import rcParams
rcParams['figure.figsize'] = 10, 6

warnings.filterwarnings('ignore', 'statsmodels.tsa.arima_model.ARIMA',

                        FutureWarning)

#page functioning
def app():
    # heading and text information
    html1 = '''
        <style>
        #heading{
        color: #E65142;
        text-align:top-left;
        font-size: 45px;
        }
        #sub_heading1{
        color: #E65142;
        text-align: right;
        font-size: 30px;
        }
        #sub_heading2{
        color: #E65142;
        text-align: left;
        font-size: 30px;
          }
        #usage_instruction{
        text-align: right;
        font-size : 15px;
        }
        #data_info{
        text-align : left;
        font-sixe : 15px;
        }
        </style>
        <h1 id = "heading"> Data Prediction </h1><br>
        '''

    st.markdown(html1, unsafe_allow_html=True)

    # Import Data
    response = requests.get("https://data.covid19.go.id/public/api/prov_detail_JAWA_TIMUR.json")
    data = json.loads(response.text)

    df = pd.json_normalize(data['list_perkembangan'])
    # print(df)

    # mengubah kolom tanggal menjadi format date
    for index, row in df.iterrows():
        temp = row['tanggal']
        row['tanggal'] = datetime.datetime.fromtimestamp(row['tanggal'] / 1000).strftime('%Y-%m-%d')
        df.replace(to_replace=temp, value=row['tanggal'], inplace=True)

    data_positif_jatim = df.groupby('tanggal')[['AKUMULASI_KASUS']].sum().reset_index()\
        .sort_values('tanggal', ascending=True).reset_index(drop=True)
    data_positif_jatim = data_positif_jatim.rename(columns={'tanggal': 'Date', 'AKUMULASI_KASUS': 'Total Cases'})
    data_positif_jatim = data_positif_jatim.set_index('Date')

    # Estimating trend
    data_positif_jatim_logScale = np.log(data_positif_jatim)
    plt.plot(data_positif_jatim_logScale)

    # The below transformation is required to make series stationary
    movingAverage = data_positif_jatim_logScale.rolling(window=12).mean()

    datasetLogScaleMinusMovingAverage = data_positif_jatim_logScale - movingAverage
    datasetLogScaleMinusMovingAverage.head(12)

    # Remove NAN values
    datasetLogScaleMinusMovingAverage.dropna(inplace=True)

    # Time Shift Transformation
    datasetLogDiffShifting = data_positif_jatim_logScale - data_positif_jatim_logScale.shift()
    datasetLogDiffShifting.dropna(inplace=True)

    # AR+I+MA = ARIMA model
    model = ARIMA(data_positif_jatim_logScale, order=(4, 1, 5))
    results_ARIMA = model.fit(disp=-1)

    # Prediction & Reverse transformations
    predictions_ARIMA_diff = pd.Series(results_ARIMA.fittedvalues, copy=True)

    # Convert to cumulative sum
    predictions_ARIMA_diff_cumsum = predictions_ARIMA_diff.cumsum()
    predictions_ARIMA_log = pd.Series(data_positif_jatim_logScale['Total Cases'].iloc[0],
                                      index=data_positif_jatim_logScale.index)
    predictions_ARIMA_log = predictions_ARIMA_log.add(predictions_ARIMA_diff_cumsum, fill_value=0)

    # Inverse of log is exp.
    predictions_ARIMA = np.exp(predictions_ARIMA_log)
    arima_plot = plt.figure()
    plt.plot(data_positif_jatim)
    plt.plot(predictions_ARIMA)
    plt.legend(['Actual', 'Forecast'])
    plt.title('Arima Performance Plot')

    html2 = '''
                <style>
                /* Rounded border */
                hr.rounded {
                    border-top: 6px solid #E65142;
                    border-radius: 5px;
                }
                </style>
                <hr class="rounded">
                <h4 id ="sub_heading2">ARIMA Model</h4>
                '''
    st.markdown(html2, unsafe_allow_html=True)
    st.write(arima_plot)
    st.write("RMSE: ", np.sqrt(metrics.mean_squared_error(data_positif_jatim, predictions_ARIMA)))

    col1, col2 = st.beta_columns(2)
    button1 = col1.button("Show Summary")


    if (button1):
        st.write(results_ARIMA.summary())
        button2 = col2.button("Hide Summary")
        if (button2):
            st.write('')

    html3 = '''
                <style>
                /* Rounded border */
                hr.rounded {
                    border-top: 6px solid #E65142;
                    border-radius: 5px;
                }
                </style>
                <hr class="rounded">
                <h4 id ="sub_heading2">ARIMA Forecasting</h4>
            '''

    st.markdown(html3, unsafe_allow_html=True)

    # Forecasting
    st.subheader('')
    days_options = range(1,31)
    days = st.select_slider("Choose how many days ahead you want to predict", options=days_options)
    st.write("Prediction(s) for ", days, "days ahead: ")

    start_index = len(data_positif_jatim_logScale)
    end_index = len(data_positif_jatim_logScale) + days
    forecast_nday = results_ARIMA.predict(start=start_index, end=end_index)
    forecast_nday_diff_cumsum = forecast_nday.cumsum()
    forecast_nday_result = np.exp(forecast_nday_diff_cumsum + float(data_positif_jatim_logScale.iloc[-1]))
    forecast_nday_result = np.ceil(forecast_nday_result)
    forecast_nday_result.rename('Total Cases', inplace=True)
    total_addition = int(forecast_nday_result[-1] - forecast_nday_result[-(days+1)])
    forecast_nday_plot = plt.figure()
    plt.plot(forecast_nday_result)

    st.write(forecast_nday_plot)
    st.write('Total addition of cases: ', str(total_addition))
    st.table(forecast_nday_result)