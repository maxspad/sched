from icalevents.icalevents import events
import datetime
from dateutil.parser import parse
import pandas as pd
import re 

def ical_to_df(ical_fn, start=None, end=None):
    start = datetime.date.today() if start is None else start
    end = parse("Jun 30 2022") if end is None else end

    es = events(file=ical_fn, start=start, end=end)

    dicts = [e.__dict__ for e in es]
    df = pd.DataFrame(dicts)
    df = df[['summary','description','start','end']]

    split_summ = df['summary'].str.split(' ')
    names = split_summ.apply(lambda x: x[-2] + ' ' + x[-1])
    
    desc_rexp = r'Group\: (.*?)\nFacility\: (.*?)\nShift\: (.*?)\nShift Type\: (.*)'
    matches = df['description'].str.extract(desc_rexp)
    matches.columns = ['group','facility','shift','type']

    df['name'] = names
    df = pd.concat([df, matches], axis=1)
    df = df[['summary','name','shift','start','end','type','facility']]
    df = df.sort_values(['start','shift'])

    print(df)
    print(df['shift'].unique())
    print(df['name'].unique())
    df.to_csv('schedule.csv')

if __name__ == "__main__":
    ical_to_df('schedule.ics')