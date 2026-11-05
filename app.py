import streamlit as st 
import pandas as pd
from streamlit_gsheets import GSheetsConnection
st.title('Liste de presence')
ecole=st.sidebar.selectbox("Choisis l'ecole", ['coranique','classique'])
if ecole=="coranique":
  section=st.sidebar.selectbox("Quel genre?", ["Homme","Femme"])
  groupe=st.sidebar.selectbox("Quel groupe",[1 , 2])
conn=st.connection("gsheets",type="GSheetsConnection")
data=conn.read()
data_filtre=data[(data["ECOLE"]==ecole) & (data["GENRE"]==section) & (data["GROUPE"]==groupe)]
st.dataframe(data_filtre)
