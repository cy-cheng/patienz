import streamlit as st 
import util.dialog as dialog
import util.constants as const
from util.tools import init_all

st.set_page_config(layout="wide")
init_all()

pages = [st.Page(f"page/{const.section_name[i]}.py", title=f"{const.noun[i]}區", icon=const.icon[i]) for i in range(len(const.noun))]

page = st.navigation(pages)
page.run()
