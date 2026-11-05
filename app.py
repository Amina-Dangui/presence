import streamlit as st 
import pandas as pd
from streamlit_gsheets import GSheetsConnection
st.title('Liste de presence')
ecole=st.sidebar.selectbox("Choisis l'ecole", ['coranique','classique'])
if ecole=="coranique":
  section=st.sidebar.selectbox("Quel genre?", ["homme","femme"])
  groupe=st.sidebar.selectbox("Quel groupe",[1 , 2])
conn=st.connection("gsheets",type=GSheetsConnection)
data=conn.read(worksheet="eleves_" + ecole, ttl=0)
if ecole=="coranique":
    data_filtre=data[(data["SECTION"]==section) & (data["GROUPE"]==groupe)]
else:                      
    data_filtre=data
jour=st.date_input("Date du jour")
st.header("Appel du jour")
statuts=["Present","Retard", "Absent" , "Absence justifiée"]
liste_eleves = data_filtre["NOM"].tolist()
historique=conn.read(worksheet="presences_" + ecole,ttl=0)
lignes=[]
for nom in liste_eleves:
    
if st.button("Enregistrer", type="primary"):
  anciennes=conn.read(worksheet="presences_" + ecole,ttl=0)
  nouvelles=pd.DataFrame(lignes)
  toutes=pd.concat([anciennes , nouvelles], ignore_index=True)
  conn.update(worksheet="presences_" + ecole, data=toutes)
  st.success("Appel Enregistré")
  
  
  


