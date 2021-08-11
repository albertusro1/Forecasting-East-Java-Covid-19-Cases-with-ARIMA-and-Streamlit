import pandas as pd
import streamlit as st
import json
import datetime
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import requests

# page functioning
def app():
    # heading and text information
    html1 = '''
    <style>
    #pred_image{

     }
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
    /* Rounded border */
    hr.rounded {
        border-top: 6px solid #E65142;
        border-radius: 5px;
    }
    </style>
    <h1 id = "heading"> Covid-19 Forecasting with ARIMA </h1>
    <h3>This website works on the data extracted from the API<br>
    <a href = "https://data.covid19.go.id/public/api/prov_detail_JAWA_TIMUR.json" target="_blank">data.covid19.go.id</a>
    </h3>
    '''
    st.markdown(html1, unsafe_allow_html=True)

    html2 = '''
    <hr class="rounded">
    <h3 id ="sub_heading2">Data Description</h3>
    <p id ="data_info">The data is the <i>covid-19 data</i> from <i>the aforementioned API.</i>
    This data originally have 9 columns with integer data type, but the data has been processed and converted into time 
    series for prediction uses.</p>
    '''
    st.markdown(html2, unsafe_allow_html=True)

    # import data
    response = requests.get("https://data.covid19.go.id/public/api/prov_detail_JAWA_TIMUR.json")
    data = json.loads(response.text)

    df = pd.json_normalize(data['list_perkembangan'])
    # print(df)

    # mengubah kolom tanggal menjadi format date
    for index, row in df.iterrows():
        temp = row['tanggal']
        row['tanggal'] = datetime.datetime.fromtimestamp(row['tanggal'] / 1000).strftime('%Y-%m-%d')
        df.replace(to_replace=temp, value=row['tanggal'], inplace=True)

    data_positif_jatim = df.groupby('tanggal')[['AKUMULASI_KASUS']].sum().reset_index().sort_values('tanggal', ascending=True).reset_index(drop=True)
    data_positif_jatim = data_positif_jatim.rename(columns={'tanggal': 'Date', 'AKUMULASI_KASUS': 'Total Cases'})
    data_positif_jatim = data_positif_jatim.set_index('Date')

    # data description
    col1, col2 = st.beta_columns(2)

    button1 = col1.button("Show Data")

    if (button1):
        st.table(data_positif_jatim)
        button2 = col2.button("Hide Data")
        if (button2):
            st.write('')

    html3 = '''
        <hr class="rounded">
        <h3 id ="sub_heading2">Data Visualization</h3>
        '''
    st.markdown(html3, unsafe_allow_html=True)

    fig = go.Figure(go.Bar(x=data_positif_jatim.index,
                           y=data_positif_jatim['Total Cases'],
                           marker_color='blue'
                           ))

    fig.update_layout(title='Total Cases of East Java',
                      template='plotly_white',
                      yaxis_title='Total Cases'
                      )
    st.write(fig)

    fig_week = go.Figure(go.Line(x=data_positif_jatim.index[-7:],
                                 y=data_positif_jatim['Total Cases'].tail(7),
                                 marker_color='blue'
                                 ))

    fig_week.update_layout(title='Cases Development in Last 7 Days',
                           template='plotly_white',
                           xaxis_title='Date',
                           yaxis_title='Total Cases'
                           )
    st.write(fig_week)
