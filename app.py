'''Main entrypoint for the application'''

import streamlit as st
from streamlit_option_menu import option_menu
import sched_consts
import sched
import feedback
import about

# This command can only be run once per streamlit app
st.set_page_config(
    page_title=sched_consts.APP_TITLE,
    page_icon="🦝",
    menu_items={
        'Get Help':None,
        "Report a Bug":None,
        "About":sched_consts.ABOUT_MARKDOWN
    }
)

# Set up the Navigation Bar
nav_bar_selected = option_menu(None, sched_consts.APP_PAGES,
    icons=['house','info-circle','card-checklist'],
    menu_icon='cast', default_index=0, orientation='horizontal')

# Display the selected page
if nav_bar_selected == "Home":
    sched.display()
elif nav_bar_selected == "About":
    about.display()
elif nav_bar_selected == 'Feedback':
    feedback.display()



