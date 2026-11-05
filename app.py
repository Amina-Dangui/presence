import streamlit as st 
import pandas as pd 
st.title('Liste de presence')
ecole=st.sidebar.selectbox("Choisis l'ecole", ['coranique','classique'])
if ecole=="coranique":
  section=st.sidebar.selectbox("Quel genre?", ["Homme","Femme"])
  groupe=st.sidebar.selectbox("Quel groupe",[1 , 2])
