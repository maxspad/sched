import streamlit as st
import sched_helpers
import pandas as pd
import numpy as np
import datetime
from sched_consts import *
from matplotlib import cm

st.set_page_config('ScheduleSteve', page_icon='favico.png')

@st.experimental_memo
def load_and_parse():
    # Download ShiftAdmin schedule
    s = sched_helpers.download_ical(CALENDAR_URL)

    # Convert to dataframe
    sched = sched_helpers.ical_to_df(s,
        start=SCHED_ICAL_START_DATE,
        end=SCHED_ICAL_END_DATE,
        tz=TZ)

    # Read in resident list
    resdf = sched_helpers.resident_df(RESIDENTS_CSV)

    # Read in off service hour listing
    osh = sched_helpers.off_service_hours_df(OFF_SERVICE_HOURS_CSV)
    
    # Generate the off-service schedule
    os_sched = sched_helpers.master_block_sched_df(MASTER_BLOCK_SCHEDULE_CSV, osh, sched, TZ)

    # Combine with the total schedule
    sched = pd.concat([sched, os_sched]).sort_index()

    return sched, resdf, os_sched, osh


sched, resdf, mbs, osh = load_and_parse()

# Define UI
cols = st.columns(2)
with cols[0]:
    st.markdown('# *ScheduleSteve*')
with cols[1]:
    st.image('raccoon.png', width=75 )
blurb = '''**Figure out when your coresidents will be off.** 

Choose the residents, a date range, and a time window when you want to plan your event.
This tool will automatically pull
the ShiftAdmin schedule and block schedule and calculate the best dates/times. 

*It\'s like a Doodle poll that fills itself out.*'''
st.markdown(blurb)
with st.expander('Options:', expanded=True):
    res_choices_holder = st.empty()
    default_resident_choices = []

    pgy_cols = st.columns(4)
    pgy_selected = [pgy_col.checkbox(f'PGY{i+1}s') for i, pgy_col in enumerate(pgy_cols)]
    for i, pgy in enumerate(pgy_selected):
        if pgy:
            default_resident_choices += resdf[resdf['year'] == (i+1)]['resident'].tolist()
    
    resident_choices = res_choices_holder.multiselect("Choose residents", resdf['resident'].tolist(), default=default_resident_choices)

    date_cols = st.columns(2)
    st_date = date_cols[0].date_input('Search between', key='st_date', 
        min_value=sched['start'].min(), max_value=sched['end'].max(),
        value=datetime.date.today())
    en_date_min_value = st_date
    en_date_min_value = sched['end'].min()
    en_date = date_cols[1].date_input('and ', key='en_date',
        min_value=st_date, max_value=sched['end'].max(),
        value=sched['end'].max())

    time_cols = st.columns(2)
    st_time = time_cols[0].time_input('for each day, show results only between the hours of', value=datetime.time(17,00))
    en_time = time_cols[1].time_input('and', key='en_time', value=datetime.time(22,00))

# Make sure residents were selected
if not len(resident_choices):
    st.info('Please select at least one resident above.')
    st.stop()

# Clean UI inputs
# Make the inputs timezone-aware
start_dt = pd.Timestamp(st_date)
start_dt = start_dt.tz_localize(TZ)
end_dt = pd.Timestamp(en_date)
end_dt = end_dt.tz_localize(TZ)

# st.write(f'Shifts between {start_dt} {start_dt.tzname()} and {end_dt} {end_dt.tzname()}') # TODO for debugging
# filter the schedule to the requested dates
fs = sched.copy()
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
hdf['dayofyear'] = [pd.Timestamp(f'{i.month}/{i.day}/{i.year}') for i in hdf.index]
hdf['hour'] = hdf.index.hour

# reformat - now rows are hours in the selcted interval and columns
# are the individual days, with cells the number of free residents
# similar to a doodle poll
free_mat = hdf.pivot(columns='dayofyear', index='hour')
free_mat.columns = free_mat.columns.droplevel(0)
free_mat.columns = [f'{c.month}/{c.day}' for c in free_mat.columns]
free_mat.columns.name = 'Date'
free_mat.index.name = 'Time'
free_mat = len(resident_choices) - free_mat

# make the index in AM/PM times to be easier to read
def fix_am_pm(x):
    if x < 12:
        return f'{x} AM'
    elif x == 12:
        return f'{x} PM'
    else:
        return f'{x-12} PM'

free_mat.index = free_mat.index.map(fix_am_pm)

# CSS to inject contained in a string
hide_dataframe_row_index = """
            <style>
            .row_heading.level0 {font-size:12pt; font-weight:bold; color:black}
            .col_heading.level0 {font-size:12pt; font-weight:bold; color:black}
            .blank {display:none}
            </style>
            """

# Inject CSS with Markdown
st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)

# style the matrix for display
free_mat_styled = (free_mat.style.background_gradient(axis=None, high=0.25, low=0.45, cmap=cm.get_cmap('RdYlGn'))
                                 .set_properties(**{'text-align':'center'})
)

# Output our dataframe and some text describing it
free_mat_df_text = '''### Best Days and Times
For each day and time, this table shows the number of residents who are free'''
st.markdown(free_mat_df_text)
st.dataframe(free_mat_styled)

# Build a table where rows are the chosen residents, columns the dates
# and cells are the shift being worked
fs = fs.sort_index()
fs['date'] = [f'{i.month}/{i.day}' for i in fs.index]
fs['shift_with_times'] = fs['shift'] # + ' (' + (fs['start'].dt.hour).apply(str) + '-' + (fs['end'].dt.hour).apply(str) + ')'
shift_mat = fs.groupby(['date','resident'])['shift_with_times'].apply(lambda x: '/'.join(x.tolist()))
shift_mat = shift_mat.reset_index()
shift_mat = shift_mat.pivot(columns='date', index='resident', values='shift_with_times')
shift_mat = shift_mat.fillna('Off')

shift_mat_styled = (shift_mat.style.set_properties(**{'font-size':'10pt'}))
# Output the df and some text describing it
shift_mat_df_text = '''### Resident Schedules
This table shows the scheduled shifts/rotations for the residents selected above'''
st.markdown(shift_mat_df_text)
st.dataframe(shift_mat_styled)
