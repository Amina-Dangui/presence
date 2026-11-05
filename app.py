import streamlit as st 
import pandas as pd
from streamlit_gsheets import GSheetsConnection
st.title('Liste de presence')
ecole=st.sidebar.selectbox("Choisis l'ecole", ['coranique','classique'])
if ecole=="coranique":
  section=st.sidebar.selectbox("Quel genre?", ["Homme","Femme"])
  groupe=st.sidebar.selectbox("Quel groupe",[1 , 2])
conn=st.connection("gsheets",type=GSheetsConnection)
data=conn.read(worksheet="eleves_" + ecole, ttl=0)
if ecole=="coranique":
    data_filtre=data[(data[(data["SECTION"]==section) & (data["GROUPE"]==groupe)]
                      else:                      
                      

