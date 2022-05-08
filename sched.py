import streamlit as st
import parse_sched
import pandas as pd
import numpy as np
import datetime
import pytz


sched = parse_sched.ical_to_df('schedule.ics')
resdf = pd.read_csv('residents.csv')


with st.expander('Options:'):
    st_date = st.date_input('Between', key='st_date')
    en_date = st.date_input('and ', key='en_date')
    st_time = st.time_input('between the hours of')
    en_time = st.time_input('and', key='en_time')
    resident_choices = st.multiselect("Residents: ", resdf['resident'].tolist())

start_dt = pd.Timestamp(st_date)
start_dt = start_dt.tz_localize('utc')
end_dt = pd.Timestamp(en_date)
end_dt = end_dt.tz_localize('utc')

blah = sched.copy().set_index('start', drop=False).sort_index()

blah = blah[start_dt:end_dt]
blah = blah[blah['resident'].isin(resident_choices)]
blah['start_day'] = blah['start'].dt.dayofyear
blah['end_day'] = blah['end'].dt.dayofyear
blah['start_hour'] = blah['start'].dt.hour
blah['end_hour'] = blah['end'].dt.hour

st.markdown('# Filtered Schedule')
blah

# initial_start = blah.iloc[0,:]['start']
initial_start = start_dt
# td = blah.iloc[-1,:]['end'] - blah.iloc[0,:]['start']
td = end_dt - start_dt
n_hours = td.total_seconds() / (60*60) # indexed by relative hour
hmat = np.zeros((len(resident_choices), int(n_hours)), dtype='int')
hdf = pd.DataFrame(hmat, index=resident_choices)

for idx, row in blah.iterrows():
    start_hour = (row['start'] - initial_start).total_seconds() / (60*60)
    end_hour = (row['end'] - initial_start).total_seconds() / (60*60)
    hdf.loc[row['resident'], start_hour:end_hour] = 1

hdf.columns = [initial_start + pd.Timedelta(hours=i) for i in range(hdf.shape[1])]

hdf = hdf.T
hdf = hdf[st_time:en_time]
# hdf['hour_of_day'] = hdf.index.hour
# hdf = hdf[(hdf['hour_of_day'] >= st_time.hour) & (hdf['hour_of_day'] <= st)
st.markdown('# Hourly Matrix')
hdf