import streamlit as st
import overview
import prediction

#Pages in the app
PAGES = {
    "Home": overview,
    "Prediction": prediction
}

#background styling
page_bg = '''
<style>
body {
background-color : #2C3539;
}
</style>
'''
st.markdown(page_bg, unsafe_allow_html=True)

#navbar styling
st.markdown(
    """
<style>
.sidebar .sidebar-content {
    background-image: linear-gradient(#292929,#E65142;9);
    color: black;
    align-text: center;
}
hr.rounded {
        border-top: 6px solid #E65142;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True,
)

#inserting image in the sidebar
st.sidebar.image('img/filkom.png', use_column_width=True)

#navbar content-1
html3 = '''
<h2 style="text-align: center;">Covid-19 Forecasting</h2>
<p style="text-align: center; font-size: 15px">This web app is designed for Covid-19 forecasting using ARIMA.</p>
<hr class="rounded">
'''
st.sidebar.markdown(html3, unsafe_allow_html=True)

st.sidebar.title("Explore")

#radio selection for the pages
selection = st.sidebar.radio("", list(PAGES.keys()))
page = PAGES[selection]
page.app()
