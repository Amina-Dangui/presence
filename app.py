import streamlit as st 
import pandas as pd
from streamlit_gsheets import GSheetsConnection
st.title(':green_book: Liste de présence')
conn = st.connection('gsheets', type=GSheetsConnection)
profs = conn.read(worksheet='profs', ttl="1h")

choix_compte = st.radio('Bienvenue !', ['Me connecter', 'Créer mon compte'], horizontal=True)

if choix_compte == 'Créer mon compte':
    nom_prof = st.text_input('Ton nom')
    nouveau_code = st.text_input('Choisis ton code', type='password')
    if st.button('Valider'):
        if nom_prof.strip() == '' or nouveau_code.strip() == '':
            st.warning('Remplis les deux cases')
        elif nouveau_code.strip() in profs['CODE'].astype(str).tolist():
            st.warning('Ce code existe déjà, choisis-en un autre')
        else:
            nouveau_prof = pd.DataFrame([{'NOM_PROF': nom_prof.strip(), 'CODE': nouveau_code.strip()}])
            profs = pd.concat([profs, nouveau_prof], ignore_index=True)
            conn.update(worksheet='profs', data=profs)
            st.cache_data.clear()
            st.success('Compte créé ! Choisis « Me connecter » en haut.')
    st.stop()

code = st.text_input('Ton code', type='password')
if code not in profs['CODE'].astype(str).tolist():
    st.info('Entre ton code pour accéder à ta liste.')
    st.stop()
ecole=st.sidebar.selectbox("Choisis l'ecole", ['coranique','classique'])
if ecole=="coranique":
  section=st.sidebar.selectbox("Quel genre?", ["homme","femme"])
  groupe=st.sidebar.selectbox("Quel groupe",[1 , 2])

tous_eleves = conn.read(worksheet="eleves_" + ecole , ttl="1h")
data=tous_eleves[tous_eleves["PROF"].astype(str)==code]
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
                eleve = {'NOM': nouveau.strip(), 'GROUPE': nv_groupe, 'SECTION': nv_section , "PROF": code}
            else:
                eleve = {'NOM': nouveau.strip() , "PROF": code}
            data = pd.concat([tous_eleves, pd.DataFrame([eleve])], ignore_index=True)
            conn.update(worksheet='eleves_' + ecole, data=data)
            st.cache_data.clear()
            st.rerun()

    st.subheader('Retirer')
    a_retirer = st.selectbox('Élève à retirer', data['NOM'].tolist(), key='retirer')
    if st.button('Retirer'):
        data = tous_eleves[~((tous_eleves['NOM'] == a_retirer) & (tous_eleves["PROF"].astype(str)==code))]
        conn.update(worksheet='eleves_' + ecole, data=data)
        st.cache_data.clear()
        st.rerun()

    
if ecole=="coranique":
    data_filtre=data[(data["SECTION"]==section) & (data["GROUPE"]==groupe)]
else:                      
    data_filtre=data
jour=st.date_input("Date du jour")
st.header(":notebook: Appel du jour")
statuts=["Present","Retard", "Absent" , "Absence justifiée"]
liste_eleves = data_filtre["NOM"].tolist()
historique=conn.read(worksheet="presences_" + ecole,ttl="1h")
historique = historique[historique["PROF"].astype(str)==code]
lignes=[]

titre1, titre2, titre3 = st.columns([2, 5, 1])
titre1.markdown('*Nom*')
titre2.markdown('*Statut*')
titre3.markdown('*Présence*')
st.divider()

for nom in liste_eleves:
    col1, col2, col3 = st.columns([2, 5, 1])

    col1.markdown('### ' + nom)
    choix = col2.radio(nom, statuts, horizontal=True, key=nom, label_visibility='collapsed')

    passe = historique[(historique['ELEVE'] == nom) & (historique["DATE"].astype(str)!= str(jour))]["STATUT"].tolist()
    tous = passe + [choix]
    presents = tous.count('Present') + tous.count('Retard')
    total = len(tous) - tous.count('Absence justifiée')
    if total > 0:
        pourcentage = round(presents / total * 100)
    else:
        pourcentage = 100

    if pourcentage >= 75:
        couleur = 'green'
    elif pourcentage >= 50:
        couleur = 'blue'
    else:
       couleur = 'red'
    col3.markdown('### :' + couleur + '[' + str(pourcentage) + ' %]')
    st.divider()

    lignes.append({'DATE': str(jour), 'ELEVE': nom, 'STATUT': choix, "PROF":code})
deja_fait=historique[(historique["DATE"].astype(str)==str(jour)) & (historique["ELEVE"].isin(liste_eleves))]
if len(deja_fait) > 0:
    st.info("L'appel de ce groupe a déjà été fait aujourd'hui.")
if st.button("Enregistrer", type="primary"):
  anciennes=conn.read(worksheet="presences_" + ecole,ttl=0)
  meme_appel = (anciennes["DATE"].astype(str)==str(jour)) &(anciennes["PROF"].astype(str)==code) & (anciennes["ELEVE"].isin(liste_eleves))
  anciennes= anciennes[~meme_appel]  
  nouvelles=pd.DataFrame(lignes)
  toutes=pd.concat([anciennes , nouvelles], ignore_index=True)
  conn.update(worksheet="presences_" + ecole, data=toutes)
  st.cache_data.clear()  
  st.success("Appel Enregistré")
    
  
  
  


