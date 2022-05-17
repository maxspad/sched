import streamlit as st
import sched_helpers
import pandas as pd
import numpy as np
import datetime
import zoneinfo
import pytz
# DEFINE GLOBAL PARAMETERS
TZ = pytz.timezone('America/Detroit')
CALENDAR_URL = 'http://www.shiftadmin.com/schedule_ical_group.php?cd=UIwfTiYhARsmldQIKdk1addmZLRORGLhbHKREh1COb8%3D&gfs=g9,f1,f2,f3&local=0&vc=1'
SCHED_ICAL_START_DATE = TZ.localize(datetime.datetime(2021, 7, 1, 0, 0, 0)).astimezone(pytz.utc)
SCHED_ICAL_END_DATE = TZ.localize(datetime.datetime(2022, 6, 30, 23, 59, 59)).astimezone(pytz.utc)
RESIDENTS_CSV = 'residents.csv'
MASTER_BLOCK_SCHEDULE_CSV = 'master_block_schedule.csv'
OFF_SERVICE_HOURS_CSV = 'off_service_hours.csv'

def load_mbs(mbs_csv_loc : str) -> pd.DataFrame:
    mbs = pd.read_csv(mbs_csv_loc, header=[0,1,2,3], index_col=0)
    mbs = mbs.T # rows are dates, columns residents
    mbs = mbs.reset_index()
    mbs.index = pd.PeriodIndex(mbs['week_start'], freq='7D') # TODO this creates an off by one bug at end of academic year
    mbs = mbs.drop(['block','week','week_start','week_end'], axis=1)

    # mbs['week_start'] = mbs['week_start'].apply(pd.Timestamp)
    # mbs['week_end'] = mbs['week_end'].apply(pd.Timestamp)
    # mbs = mbs.set_index('week_start')

    # mbs = mbs.set_index(['week_start', 'week_end', 'week', 'block'], drop=True)
    return mbs

# @st.experimental_memo
def load_and_parse():
    # Download ShiftAdmin schedule
    s = sched_helpers.download_ical(CALENDAR_URL)
    # Convert to dataframe
    sched = sched_helpers.ical_to_df(s,
        start=SCHED_ICAL_START_DATE,
        end=SCHED_ICAL_END_DATE,
        tz=TZ)
    # Read in resident list
    resdf = pd.read_csv(RESIDENTS_CSV)
    # Read in block schedule
    # mbs = pd.read_csv(MASTER_BLOCK_SCHEDULE_CSV, header=[0,1,2,3], index_col=0)
    mbs = load_mbs(MASTER_BLOCK_SCHEDULE_CSV)
    # Read in off service hour listing
    osh = pd.read_csv(OFF_SERVICE_HOURS_CSV)
    osh = osh.set_index('rotation')
    return sched, resdf, mbs, osh


sched, resdf, mbs, osh = load_and_parse()
print(mbs.index)
mbs_starts = mbs.replace(osh['start'].to_dict())
mbs_starts['col_type'] = 'start'
mbs_ends = mbs.replace(osh['end'].to_dict())
mbs_ends['col_type'] = 'end'
mbs['col_type'] = 'shift'
mbs = pd.concat([mbs_starts, mbs_ends, mbs])
mbs = mbs.pivot(columns='col_type')
mbs = mbs.resample('D').ffill()
mbs = mbs.sort_index()
# st.write(osh['start'].to_dict())
print(mbs)
# st.dataframe(mbs.apply(lambda x: x.apply(lambda yosh.loc[x,'start'], axis=0))

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
# Make the inputs timezone-aware
start_dt = pd.Timestamp(st_date)
start_dt = start_dt.tz_localize(TZ)
end_dt = pd.Timestamp(en_date)
end_dt = end_dt.tz_localize(TZ)

st.write(f'Shifts between {start_dt} {start_dt.tzname()} and {end_dt} {end_dt.tzname()}') # TODO for debugging
# filter the schedule to the requested dates
fs = sched.copy()
fs = fs[start_dt:end_dt]

# filter the schedule to the requested residents
st.write(f'For residents {" ".join(resident_choices)}') # TODO for debugging
fs = fs[fs['resident'].isin(resident_choices)]

st.write('Filtered schedule:') # TODO for debugging
st.dataframe(fs)
# add some extra columns to make things easier 
fs['start_day'] = fs['start'].dt.dayofyear
fs['end_day'] = fs['end'].dt.dayofyear
fs['start_hour'] = fs['start'].dt.hour
fs['end_hour'] = fs['end'].dt.hour

# add in off service rotations
# mbs = mbs.drop(['block','week','week_end'], axis=1)
# mbs

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
