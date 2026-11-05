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
with st.sidebar.expander('Gérer les élèves'):
    st.subheader('Ajouter')
    nouveau = st.text_input('Nom du nouvel élève')
    if ecole == 'coranique':
        nv_section = st.selectbox('Genre', ['femme', 'homme'], key='nv_section')
        nv_groupe = st.selectbox('Groupe', [1, 2], key='nv_groupe')
    if st.button('Ajouter'):
        if nouveau.strip() == '':
            st.warning('Écris un nom')
        else:
            if ecole == 'coranique':
                eleve = {'NOM': nouveau.strip(), 'GROUPE': nv_groupe, 'SECTION': nv_section}
            else:
                eleve = {'NOM': nouveau.strip()}
            data = pd.concat([data, pd.DataFrame([eleve])], ignore_index=True)
            conn.update(worksheet='eleves_' + ecole, data=data)
            st.rerun()

    st.subheader('Retirer')
    a_retirer = st.selectbox('Élève à retirer', data['NOM'].tolist(), key='retirer')
    if st.button('Retirer'):
        data = data[data['NOM'] != a_retirer]
        conn.update(worksheet='eleves_' + ecole, data=data)
       with st.sidebar.expander('Gérer les élèves'):
    st.subheader('Ajouter')
    nouveau = st.text_input('Nom du nouvel élève')
    if ecole == 'coranique':
        nv_section = st.selectbox('Genre', ['femme', 'homme'], key='nv_section')
        nv_groupe = st.selectbox('Groupe', [1, 2], key='nv_groupe')
    if st.button('Ajouter'):
        if nouveau.strip() == '':
            st.warning('Écris un nom')
        else:
            if ecole == 'coranique':
                eleve = {'NOM': nouveau.strip(), 'GROUPE': nv_groupe, 'SECTION': nv_section}
            else:
                eleve = {'NOM': nouveau.strip()}
            data = pd.concat([data, pd.DataFrame([eleve])], ignore_index=True)
            conn.update(worksheet='eleves_' + ecole, data=data)
            st.rerun()

    st.subheader('Retirer')
    a_retirer = st.selectbox('Élève à retirer', data['NOM'].tolist(), key='retirer')
    if st.button('Retirer'):
        data = data[data['NOM'] != a_retirer]
        conn.update(worksheet='eleves_' + ecole, data=data)
        st.rerun()
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
    titre1, titre2, titre3 = st.columns([2, 5, 1])
titre1.markdown('*Nom*')
titre2.markdown('*Statut*')
titre3.markdown('*Présence*')
st.divider()

for nom in liste_eleves:
    col1, col2, col3 = st.columns([2, 5, 1])

    col1.markdown('### ' + nom)
    choix = col2.radio(nom, statuts, horizontal=True, key=nom, label_visibility='collapsed')

    passe = historique[historique['ELEVE'] == nom]['STATUT'].tolist()
    tous = passe + [choix]
    presents = tous.count('Present') + tous.count('Retard')
    total = len(tous) - tous.count('Absence justifiée')
    if total > 0:
        pourcentage = round(presents / total * 100)
    else:
        pourcentage = 100

    col3.markdown('### ' + str(pourcentage) + ' %')
    st.divider()

    lignes.append({'DATE': str(jour), 'ELEVE': nom, 'STATUT': choix})
if st.button("Enregistrer", type="primary"):
  anciennes=conn.read(worksheet="presences_" + ecole,ttl=0)
  nouvelles=pd.DataFrame(lignes)
  toutes=pd.concat([anciennes , nouvelles], ignore_index=True)
  conn.update(worksheet="presences_" + ecole, data=toutes)
  st.success("Appel Enregistré")
  
  
  


