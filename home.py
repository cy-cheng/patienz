import streamlit as st 
import util.dialog as dialog
import util.constants as const

st.set_page_config(layout="wide")

pages = [st.Page(f"page/{const.section_name[i]}.py", title=f"{const.noun[i]}區", icon=const.icon[i]) for i in range(len(const.noun))]

page = st.navigation(pages)
page.run()
