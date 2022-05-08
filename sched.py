import streamlit as st
import datetime
import numpy as np
import pandas as pd

st.markdown('# Choose a date')
with st.expander('Options:'):
    st_date = st.date_input('Between', key='st_date')
    en_date = st.date_input('and ', key='en_date')
    st_time = st.time_input('between the hours of')
    en_time = st.time_input('and', key='en_time')
st.write(['You chose', st_date, 'and', en_date])