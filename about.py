from collections import OrderedDict
import streamlit as st
import sched_consts as sc
import pandas as pd

osh = pd.read_csv('data/off_service_hours.csv')

faqs = [
    (
        f'How does {sc.APP_TITLE} work?',
        f'''{sc.APP_TITLE} starts by downloading the ED schedule for UM, SJ, and Hurley from ShiftAdmin.
Then, it augments it by adding in all the residents who are on off service rotations. To do this, it
processes a hand-coded version of the master block schedule for the program, organized by week. Each
off-service rotation corresponds to a specific "shift time." For example, the CCMU is generally from 
5:30AM to 8PM. By filling in these "shift times" for the off-service rotations, the app makes "dummy shifts"
for residents in off-service rotations.

Over the specific time period requested by the user for the specific residents requested, it goes hour-by-hour,
totaling the number of residents who are *not* on shift (in the ED or off service), and reporting the results.''',
        False
    ),

    (
        f'What are {sc.APP_TITLE}\'s limitations?',
        f'''Because all the off-service rotations list their schedules in so many different ways (ShiftAdmin,
Amion, random excel spreadsheets), it's impossible to fully integrate them into {sc.APP_TITLE}. For example,
{sc.APP_TITLE} considers PICU to run from 6AM to 5PM every day; it can't tell when PICU nights (🤮) are. 

That's part of why the shift schedule is given below the residents-off table; so that you can see when people
might be off service and when the results might not be 100% accurate.''',
        False
    ),

    (
        f'How does {sc.APP_TITLE} know when off-service rotations start/end?',
        f'''{sc.APP_TITLE} knows *when* a resident is on an off-service rotation by looking up the residents schedule in 
    a hand-coded version of the master block schedule. To know what *hours* the resident is working while on that
    rotation, it uses a lookup table based on my best guess/memory of the rotation's hours. You can see that 
    table below:

{osh.to_html()}
        ''',
        False
    ),

    (
        f'I think this is great! / I have ideas for improvement / I found a bug! 🪲',
        f'''Awesome! Let me know via the "Feedback" tab above.''',
        False
    )
]


about_app = f'''
# About {sc.APP_TITLE}
As EM residents, we tend to get more time off than our non-EM counterparts, but
finding  ways to actually *use* that time off together is tricky due to the disjointed
nature of our schedules. It's hard enough to keep track of your own schedule, trying
to reconcile it with a friend's or your whole class's schedule is impossible.

Doodle works but its slow and requires people to do extra work an we hate that. 

So I wrote this app to try and making *using* our slightly more abundant, if oddly-scheduled,
free time a little easier. I hope you like it!

💙 Max
'''

def display():
    st.markdown(about_app)
    st.markdown('## FAQs')
    for title, content, expanded in faqs:
        expander = st.expander(title, expanded=expanded)
        expander.markdown(f'#### {title}\n{content}', unsafe_allow_html=True)