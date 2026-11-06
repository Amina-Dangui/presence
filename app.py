import streamlit as st 
import pandas as pd
from fpdf import FPDF
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
        elif nouveau.strip() in data['NOM'].astype(str).tolist():
            st.warning(nouveau.strip() + ' existe déjà. Ajoute une précision, par exemple ' + nouveau.strip() + ' B.')    
        else:
            if ecole == 'coranique':
                eleve = {'NOM': nouveau.strip(), 'GROUPE': nv_groupe, 'SECTION': nv_section , "PROF": code}
            else:
                eleve = {'NOM': nouveau.strip() , "PROF": code}
            data = pd.concat([tous_eleves, pd.DataFrame([eleve])], ignore_index=True)
            conn.update(worksheet='eleves_' + ecole, data=data)
            st.cache_data.clear()
            st.rerun()
            
    st.subheader('Ajouter plusieurs élèves')
    liste_noms = st.text_area('Un nom par ligne')
    if st.button('Ajouter la liste'):
        noms = [n.strip() for n in liste_noms.split('\n') if n.strip() != '']
        if len(noms) == 0:
            st.warning('Écris au moins un nom')
        else:
            nouveaux = []
            for n in noms:
                if ecole == 'coranique':
                    nouveaux.append({'NOM': n, 'GROUPE': nv_groupe, 'SECTION': nv_section, 'PROF': code})
                else:
                    nouveaux.append({'NOM': n, 'PROF': code})
            data = pd.concat([tous_eleves, pd.DataFrame(nouveaux)], ignore_index=True)
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
st.header(":memo: Appel du jour")
resume=st.empty()
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
statuts_du_jour = [l['STATUT'] for l in lignes]
nb_presents = statuts_du_jour.count('Present')
nb_retards = statuts_du_jour.count('Retard')
nb_absents = statuts_du_jour.count('Absent')
nb_justifies = statuts_du_jour.count('Absence justifiée')
texte_resume = ':white_check_mark: ' + str(nb_presents) + ' présents'
texte_resume = texte_resume + ' · :clock3: ' + str(nb_retards) + ' retards'
texte_resume = texte_resume + ' · :x: ' + str(nb_absents) + ' absents'
texte_resume = texte_resume + ' · :page_facing_up: ' + str(nb_justifies) + ' justifiés'
resume.info(texte_resume)    
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

st.divider()
st.subheader(':green_book: Exporter en PDF')

pdf = FPDF()
pdf.add_page()
pdf.set_font('Helvetica', 'B', 16)
pdf.cell(0, 10, 'Liste de présence - école ' + ecole, new_x='LMARGIN', new_y='NEXT')
pdf.set_font('Helvetica', '', 11)
pdf.cell(0, 8, 'Document créé le ' + str(jour), new_x='LMARGIN', new_y='NEXT')
pdf.ln(4)

pdf.set_font('Helvetica', 'B', 11)
pdf.cell(55, 8, 'Nom', border=1)
pdf.cell(25, 8, 'Présents', border=1)
pdf.cell(25, 8, 'Retards', border=1)
pdf.cell(25, 8, 'Absents', border=1)
pdf.cell(25, 8, 'Justifiés', border=1)
pdf.cell(30, 8, 'Présence', border=1, new_x='LMARGIN', new_y='NEXT')

pdf.set_font('Helvetica', '', 11)
for nom in liste_eleves:
    statuts_eleve = historique[historique['ELEVE'] == nom]['STATUT'].tolist()
    p = statuts_eleve.count('Present')
    r = statuts_eleve.count('Retard')
    a = statuts_eleve.count('Absent')
    j = statuts_eleve.count('Absence justifiée')
    total_eleve = len(statuts_eleve) - j
    if total_eleve > 0:
        pct = round((p + r) / total_eleve * 100)
    else:
        pct = 100
    pdf.cell(55, 8, str(nom), border=1)
    pdf.cell(25, 8, str(p), border=1)
    pdf.cell(25, 8, str(r), border=1)
    pdf.cell(25, 8, str(a), border=1)
    pdf.cell(25, 8, str(j), border=1)
    pdf.cell(30, 8, str(pct) + ' %', border=1, new_x='LMARGIN', new_y='NEXT')

fichier_pdf = bytes(pdf.output())
st.download_button('Télécharger en PDF', data=fichier_pdf, file_name='presences_' + ecole + '.pdf', mime='application/pdf')
    
  
  
  


