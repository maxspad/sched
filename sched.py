import streamlit as st
import parse_sched
import pandas as pd
import numpy as np
import datetime
import pytz

import urllib.request

# CALENDAR_URL = 'http://www.shiftadmin.com/schedule_ical_group.php?cd=UIwfTiYhARsmldQIKdk1addmZLRORGLhbHKREh1COb8%3D&gfs=g9,f1,f2,f3&local=1&vc=1'

# s = urllib.request.urlopen(CALENDAR_URL).read()

# patch over with no internet connection
with open('schedule.ics') as f:
    s = bytes(f.read(), encoding='utf-8')


# Read in schedule
sched = parse_sched.ical_to_df(s,
    start=datetime.datetime(2021, 7, 1, 0, 0, 0),
    end=datetime.datetime(2022, 6, 30, 23, 59, 59))
resdf = pd.read_csv('residents.csv')

# Define UI
with st.expander('Options:'):
    st_date = st.date_input('Between', key='st_date', 
        min_value=sched['start'].min(), max_value=sched['end'].max(),
        value=datetime.date.today())
    en_date = st.date_input('and ', key='en_date',
        min_value=sched['end'].min(), max_value=sched['end'].max(),
        value=sched['end'].max())
    st_time = st.time_input('between the hours of', value=datetime.time(15,00))
    en_time = st.time_input('and', key='en_time', value=datetime.time(23,00))
    resident_choices = st.multiselect("Residents: ", resdf['resident'].tolist(),
        default=['M Spadafore','M Newton', 'M Basinger'])

# Clean UI inputs
# Add the timezone to the inputs
start_dt = pd.Timestamp(st_date)
start_dt = start_dt.tz_localize('utc')
end_dt = pd.Timestamp(en_date)
end_dt = end_dt.tz_localize('utc')

# filter the schedule to the requested dates
fs = sched.copy().set_index('start', drop=False).sort_index()
fs = fs[start_dt:end_dt]

# filter the schedule to the requested residents
fs = fs[fs['resident'].isin(resident_choices)]

# add some extra columns to make things easier 
fs['start_day'] = fs['start'].dt.dayofyear
fs['end_day'] = fs['end'].dt.dayofyear
fs['start_hour'] = fs['start'].dt.hour
fs['end_hour'] = fs['end'].dt.hour

# Build a matrix where rows are residents and columns are hours
# 0-hour/column is the first hour (midnight) of start_dt
# the value of the matrix at res,hr is 1 if the resident is working
# at that hour
td = end_dt - start_dt # the total time span
n_hours = td.total_seconds() / (60*60) # indexed by relative hour
hmat = np.zeros((len(resident_choices), int(n_hours)), dtype='int')
hdf = pd.DataFrame(hmat, index=resident_choices)

for idx, row in fs.iterrows():
    start_hour = (row['start'] - start_dt).total_seconds() / (60*60)
    end_hour = (row['end'] - start_dt).total_seconds() / (60*60)
    # if the resident is working during those hours aka there's a row
    # in fs, hdf's value is 1
    hdf.loc[row['resident'], start_hour:end_hour] = 1

# Switch back from relative hours to actual hours
hdf.columns = [start_dt + pd.Timedelta(hours=i) for i in range(hdf.shape[1])]
hdf = hdf.T # transpose for convenience

# filter to include only the selected times
hdf = hdf[st_time:en_time]


# for each hour-long time period, sum the number of selected residents working 
# during the time period
hdf['n_working'] = hdf.sum(1)
hdf.index.name = 'time'
hdf = hdf[['n_working']] # filter to only be the aggregated column
hdf['dayofyear'] = [f'{i.month}/{i.day}' for i in hdf.index]
hdf['hour'] = hdf.index.hour

# reformat - now rows are hours in the selcted interval and columns
# are the individual days, with cells the number of free residents
# similar to a doodle poll
free_mat = hdf.pivot(columns='dayofyear', index='hour')
free_mat.columns = free_mat.columns.droplevel(0)
free_mat.columns.name = 'Date'
free_mat.index.name = 'Time'
free_mat = len(resident_choices) - free_mat
st.dataframe(free_mat)

# Build a table where rows are the chosen residents, columns the dates
# and cells are the shift being worked
fs = fs.sort_index()
fs['date'] = [f'{i.month}/{i.day}' for i in fs.index]
fs['shift_with_times'] = fs['shift'] + ' (' + (fs['start'].dt.hour).apply(str) + '-' + (fs['end'].dt.hour).apply(str) + ')'
shift_mat = fs.groupby(['date','resident'])['shift_with_times'].apply(lambda x: '/'.join(x.tolist()))
shift_mat = shift_mat.reset_index()
shift_mat = shift_mat.pivot(columns='date', index='resident', values='shift_with_times')
shift_mat = shift_mat.fillna('Off')
shift_mat
