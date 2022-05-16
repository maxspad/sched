from icalevents.icalevents import events
import datetime
from dateutil.parser import parse
import pandas as pd
import pytz
import urllib

def download_ical(url : str, from_file=False) -> str:
    if not from_file:
        s = urllib.request.urlopen(url).read()
    else:
        with open(url) as f:
            s = bytes(f.read(), encoding='utf-8')
    return s
    


def ical_to_df(ical_str : str, start : datetime.date = None, end : datetime.date = None,
    tz=pytz.utc):
    start = datetime.date.today() if start is None else start # default to today
    end = parse("Jun 30 2022") if end is None else end # default to end of the academic year 

    es = events(string_content=ical_str, start=start, end=end)

    dicts = [e.__dict__ for e in es]
    df = pd.DataFrame(dicts)
    df = df[['summary','description','start','end']]

    split_summ = df['summary'].str.split(' ')
    names = split_summ.apply(lambda x: x[-2] + ' ' + x[-1])
    
    desc_rexp = r'Group\: (.*?)\nFacility\: (.*?)\nShift\: (.*?)\nShift Type\: (.*)'
    matches = df['description'].str.extract(desc_rexp)
    matches.columns = ['group','facility','shift','type']

    df['resident'] = names
    df = pd.concat([df, matches], axis=1)
    df = df[['summary','resident','shift','start','end','type','facility']]

    # convert to the specified timezone and reindex
    df = df.sort_values(['start','shift'])
    df = df.set_index('start', drop=False)
    df.index = df.index.tz_convert(tz)

    return df

def resident_list(sched_df : pd.DataFrame):
    return list(sched_df['resident'].unique())

if __name__ == "__main__":
    sched_df = ical_to_df('schedule.ics')
    res_list = resident_list(sched_df)
    with open('res_list.txt','w') as f:
        f.writelines([r + '\n' for r in res_list])
