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
  col1, col2 = st.columns([3,1])
  with col1:
    choix=st.radio(nom,statuts,horizontal=True, key=nom)
    passe=historique[historique["ELEVE"]==nom]["STATUT"].tolist()
    tous=passe + [choix]
    presents=tous.count("Present") + tous.count("Retard")
    total=len(tous)-tous.count("Absence justifée")
    if total> 0:
        pourcentage=round(presents/total*100)
    else:
        pourcentage=100
    with col2:
      st.metric("Presence", str(pourcentage) + " % ")
    lignes.append({"DATE":str(jour),"ELEVE":nom, "STATUT":choix})  
if st.button("Enregistrer", type="primary"):
  anciennes=conn.read(worksheet="presences_" + ecole,ttl=0)
  nouvelles=pd.DataFrame(lignes)
  toutes=pd.concat([anciennes , nouvelles], ignore_index=True)
  conn.update(worksheet="presences_" + ecole, data=toutes)
  st.success("Appel Enregistré")
  
  
  


