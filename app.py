import streamlit as st
from IPython.core.display import display_html
with open("./home.md","r") as home:
    home_content = home.read()

st.markdown(home_content,unsafe_allow_html=True)

view = [100,150,30]
st.write('Youtube view')
view

st.bar_chart(view)
