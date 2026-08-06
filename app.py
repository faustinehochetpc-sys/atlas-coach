import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import json
import requests

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Atlas - Licence Gestion", page_icon="🎓", layout="wide")

# --- DONNÉES DE LA MAQUETTE PÉDAGOGIQUE (Crédits ECTS & Coefficients) ---
MAQUETTE_LICENCE_GESTION = {
    "S1": [
        {"code": "120-1-11", "nom": "Introduction aux sciences de gestion", "ects": 5, "coeff": 5},
        {"code": "120-1-12", "nom": "Histoire de la pensée et des techniques managériales", "ects": 3, "coeff": 3},
        {"code": "120-1-21", "nom": "Introduction au droit", "ects": 3, "coeff": 3},
        {"code": "120-1-22", "nom": "Théories économiques et enjeux contemporains", "ects": 4, "coeff": 4},
        {"code": "120-1-31", "nom": "Micro-économie", "ects": 3, "coeff": 3},
        {"code": "120-1-32", "nom": "Expression écrite et orale", "ects": 2, "coeff": 2},
        {"code": "120-1-33", "nom": "Fondamentaux de comptabilité", "ects": 4, "coeff": 4},
        {"code": "120-1-01", "nom": "Informatique d'usage", "ects": 2, "coeff": 2},
        {"code": "120-1-02", "nom": "LV1 Anglais", "ects": 2, "coeff": 2},
        {"code": "120-1-03", "nom": "Accompagnement à la réussite de mon projet 1", "ects": 2, "coeff": 2}
    ],
    "S2": [
        {"code": "120-2-11", "nom": "Comptabilité générale", "ects": 5, "coeff": 5},
        {"code": "120-2-12", "nom": "Statistiques pour gestionnaires 1", "ects": 4, "coeff": 4},
        {"code": "120-2-21", "nom": "Droit commercial", "ects": 4, "coeff": 4},
        {"code": "120-2-22", "nom": "Marketing : histoire et réalités contemporaines", "ects": 3, "coeff": 3},
        {"code": "120-2-23", "nom": "Négociation commerciale", "ects": 4, "coeff": 4},
        {"code": "120-2-41", "nom": "Géopolitique (Choix)", "ects": 3, "coeff": 3},
        {"code": "120-2-42", "nom": "Sociologie de la consommation (Choix)", "ects": 3, "coeff": 3},
        {"code": "120-2-52", "nom": "Expression et culture managériale en espagnol (Choix)", "ects": 3, "coeff": 3},
        {"code": "120-2-53", "nom": "Expression et culture managériale en allemand (Choix)", "ects": 3, "coeff": 3},
        {"code": "120-2-01", "nom": "Informatique d'usage", "ects": 2, "coeff": 2},
        {"code": "120-2-02", "nom": "LV1 Anglais", "ects": 2, "coeff": 2}
    ],
    "S3": [
        {"code": "120-3-11", "nom": "Marketing stratégique", "ects": 4, "coeff": 4},
        {"code": "120-3-12", "nom": "Techniques quantitatives de gestion", "ects": 4, "coeff": 4},
        {"code": "120-3-13", "nom": "Statistiques pour gestionnaires 2", "ects": 5, "coeff": 5},
        {"code": "120-3-21", "nom": "Droit social", "ects": 4, "coeff": 4},
        {"code": "120-3-22", "nom": "Droit des sociétés", "ects": 4, "coeff": 4},
        {"code": "120-3-42", "nom": "Le manager face aux défis du numérique (Choix)", "ects": 3, "coeff": 3},
        {"code": "120-3-41", "nom": "Théorie des organisations (Choix)", "ects": 3, "coeff": 3},
        {"code": "120-3-51", "nom": "International trades (Choix)", "ects": 2, "coeff": 2},
        {"code": "120-3-52", "nom": "Sales and negotiation (Choix)", "ects": 2, "coeff": 2},
        {"code": "120-3-53", "nom": "Entorno de los negocios Espana y Latinoamérica (Choix)", "ects": 2, "coeff": 2},
        {"code": "120-3-54", "nom": "Expression et culture managériale en allemand (Choix)", "ects": 2, "coeff": 2},
        {"code": "120-3-01", "nom": "LV1 Anglais", "ects": 2, "coeff": 2},
        {"code": "120-3-02", "nom": "Accompagnement à la réussite de mon projet 2", "ects": 1, "coeff": 1}
    ],
    "S4": [
        {"code": "120-4-11", "nom": "Comptabilité de gestion", "ects": 5, "coeff": 5},
        {"code": "120-4-12", "nom": "Marketing opérationnel", "ects": 4, "coeff": 4},
        {"code": "120-4-21", "nom": "Droit fiscal", "ects": 3, "coeff": 3},
        {"code": "120-4-22", "nom": "Mathématiques financières", "ects": 3, "coeff": 3},
        {"code": "120-4-31", "nom": "Technologies du web", "ects": 3, "coeff": 3},
        {"code": "120-4-32", "nom": "Projet", "ects": 2, "coeff": 2},
        {"code": "120-4-42", "nom": "Entrepreneuriat (Choix)", "ects": 3, "coeff": 3},
        {"code": "120-4-41", "nom": "Management de l'innovation (Choix)", "ects": 3, "coeff": 3},
        {"code": "120-4-51", "nom": "Introduction to international marketing (Choix)", "ects": 2, "coeff": 2},
        {"code": "120-4-52", "nom": "Management and environment (Choix)", "ects": 2, "coeff": 2},
        {"code": "120-4-53", "nom": "Comercio internacional 1 (Choix)", "ects": 2, "coeff": 2},
        {"code": "120-4-54", "nom": "Actualité économique, politique, sociale en allemand (Choix)", "ects": 2, "coeff": 2},
        {"code": "120-4-01", "nom": "LV1 Anglais", "ects": 2, "coeff": 2},
        {"code": "120-4-02", "nom": "Business game", "ects": 2, "coeff": 2}
    ]
}

# --- INITIALISATION DES VARIABLES EN SESSION ---
if "cards_data" not in st.session_state:
    st.session_state.cards_data = {
        sem: {m["nom"]: [] for m in MAQUETTE_LICENCE_GESTION[sem]} for sem in MAQUETTE_LICENCE_GESTION
    }

if "notes_data" not in st.session_state:
    st.session_state.notes_data = {
        sem: {m["nom"]: 0.0 for m in MAQUETTE_LICENCE_GESTION[sem]} for sem in MAQUETTE_LICENCE_GESTION
    }

if "card_index" not in st.session_state:
    st.session_state.card_index = 0

if "show_answer" not in st.session_state:
    st.session_state.show_answer = False

# --- BARRE LATÉRALE ---
st.sidebar.title("🎓 Atlas - Licence Gestion")

# 1. Clé API Gemini
api_key = st.sidebar.text_input("Clé API Google Gemini", type="password")
if api_key:
    genai.configure(api_key=api_key)

st.sidebar.divider()

# 2. Webhook n8n
n8n_webhook_url = st.sidebar.text_input("URL Webhook n8n (Optionnel)", placeholder="https://votre-n8n.com/webhook/atlas")

st.sidebar.divider()

# 3. Navigation Semestre & Matière
semestre_selectionne = st.sidebar.selectbox("Sélectionner le Semestre", ["S1", "S2", "S3", "S4"])

matieres_disponibles = list(st.session_state.cards_data[semestre_selectionne].keys())
matiere_selectionnee = st.sidebar.selectbox("Matière active", matieres_disponibles if matieres_disponibles else ["Aucune"])

st.sidebar.divider()

# 4. Choix du Mode
mode = st.sidebar.radio("Module", ["Cours & IA", "Flashcards", "QCM", "Moyennes & ECTS", "n8n & Automatisations", "Sauvegardes"])

# --- HEADER PRINCIPAL ---
st.title(f"Atlas 🗺️ - {semestre_selectionne} > {matiere_selectionnee}")

# --- FONCTION DE COMMUNICATION AVEC N8N ---
def call_n8n(action_name, payload=None):
    if not n8n_webhook_url:
        st.error("Veuillez renseigner votre URL Webhook n8n dans le menu latéral.")
        return None
    try:
        res = requests.post(n8n_webhook_url, json={"action": action_name, "payload": payload or {}})
        if res.status_code == 200:
            return res.json()
        st.error(f"Erreur Webhook ({res.status_code}) : {res.text}")
    except Exception as e:
        st.error(f"Erreur de connexion n8n : {e}")
    return None

# --- MODULE 1 : COURS & IA ---
if mode == "Cours & IA":
    st.subheader("Analyse de cours et Génération automatique de Flashcards par IA")
    
    uploaded_file = st.file_uploader("Importer le cours (PDF)", type=["pdf"])
    prompt_custom = st.text_area("Consigne ou question pour l'IA :", "Fais un résumé synthétique des éléments clés.")

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💬 Interroger Atlas sur ce cours", use_container_width=True):
            if not api_key:
                st.error("Ajoutez la clé API Gemini dans le menu latéral.")
            else:
                txt = ""
                if uploaded_file:
                    reader = PdfReader(uploaded_file)
                    for page in reader.pages:
                        txt += page.extract_text() or ""
                
                content = f"Document : {txt}\n\nConsigne : {prompt_custom}" if txt else prompt_custom
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(content)
                    st.markdown("### Réponse d'Atlas :")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Erreur : {e}")

    with col2:
        if st.button("✨ Générer automatiquement des Flashcards", use_container_width=True):
            if not api_key:
                st.error("Ajoutez la clé API Gemini dans le menu latéral.")
            else:
                txt = ""
                if uploaded_file:
                    reader = PdfReader(uploaded_file)
                    for page in reader.pages:
                        txt += page.extract_text() or ""
                
                if not txt and not prompt_custom:
                    st.warning("Veuillez téléverser un cours PDF ou rédiger un texte.")
                else:
                    with st.spinner("Atlas analyse et génère les questions..."):
                        p_flash = f"""
                        Génère 5 flashcards au format JSON strict sur le cours suivant.
                        Format attendu : [{"{"}"q": "Question", "a": "Réponse"{"}"}]
                        
                        Cours : {txt if txt else prompt_custom}
                        """
                        try:
                            model = genai.GenerativeModel('gemini-1.5-pro')
                            res = model.generate_content(p_flash)
                            clean = res.text.replace("```json", "").replace("```", "").strip()
                            new_cards = json.loads(clean)
                            
                            st.session_state.cards_data[semestre_selectionne][matiere_selectionnee].extend(new_cards)
                            st.success(f"{len(new_cards)} Flashcards créées dans {matiere_selectionnee} !")
                        except Exception as e:
                            st.error(f"Impossible de traiter les cartes : {e}")

# --- MODULE 2 : FLASHCARDS ---
elif mode == "Flashcards":
    st.subheader("Révisions interactives")
    cartes = st.session_state.cards_data[semestre_selectionne].get(matiere_selectionnee, [])
    
    if not cartes:
        st.info("Aucune carte enregistrée. Créez-en une manuellement ou générez-en depuis le module Cours & IA.")
    else:
        idx = st.session_state.card_index % len(cartes)
        c = cartes[idx]

        st.markdown(f"**Carte {idx + 1} / {len(cartes)}**")
        with st.container(border=True):
            st.markdown(f"### ❓ Question :\n{c['q']}")
            if st.session_state.show_answer:
                st.divider()
                st.markdown(f"### 💡 Réponse :\n{c['a']}")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("👁️ Afficher / Masquer Réponse", use_container_width=True):
                st.session_state.show_answer = not st.session_state.show_answer
                st.rerun()
        with c2:
            if st.button("➡️ Carte Suivante", use_container_width=True):
                st.session_state.card_index += 1
                st.session_state.show_answer = False
                st.rerun()

    st.divider()
    st.write("#### Ajout manuel")
    q_in = st.text_input("Question")
    a_in = st.text_input("Réponse")
    if st.button("Ajouter la carte") and q_in and a_in:
        st.session_state.cards_data[semestre_selectionne][matiere_selectionnee].append({"q": q_in, "a": a_in})
        st.success("Carte ajoutée !")
        st.rerun()

# --- MODULE 3 : QCM ---
elif mode == "QCM":
    st.subheader("Auto-évaluation QCM")
    cartes = st.session_state.cards_data[semestre_selectionne].get(matiere_selectionnee, [])
    
    if not cartes:
        st.info("Il faut au moins une question enregistrée dans cette matière pour démarrer un QCM.")
    else:
        q_item = cartes[st.session_state.card_index % len(cartes)]
        st.write(f"### Question : {q_item['q']}")
        rep = st.radio("Options :", [q_item['a'], "Option B (Incorrecte)", "Option C (Incorrecte)"])
        
        if st.button("Valider la réponse"):
            if rep == q_item['a']:
                st.success("Excellente réponse !")
            else:
                st.error("Mauvaise réponse.")

# --- MODULE 4 : MOYENNES & ECTS ---
elif mode == "Moyennes & ECTS":
    st.subheader(f"Calcul des moyennes pondérées par crédits ECTS ({semestre_selectionne})")
    
    matieres_sem = MAQUETTE_LICENCE_GESTION[semestre_selectionne]
    total_points = 0.0
    total_coefficients = 0.0
    total_ects_obtenus = 0

    col_mats = st.columns(2)
    for index, mat in enumerate(matieres_sem):
        with col_mats[index % 2]:
            note = st.number_input(
                f"{mat['nom']} (ECTS: {mat['ects']} | Coeff: {mat['coeff']})",
                min_value=0.0, max_value=20.0,
                value=float(st.session_state.notes_data[semestre_selectionne].get(mat['nom'], 0.0)),
                step=0.5,
                key=f"note_{semestre_selectionne}_{mat['code']}"
            )
            st.session_state.notes_data[semestre_selectionne][mat['nom']] = note
            
            total_points += note * mat['coeff']
            total_coefficients += mat['coeff']
            if note >= 10.0:
                total_ects_obtenus += mat['ects']

    moyenne_semestre = total_points / total_coefficients if total_coefficients > 0 else 0.0

    st.divider()
    c_res1, c_res2 = st.columns(2)
    with c_res1:
        st.metric(label=f"Moyenne générale {semestre_selectionne}", value=f"{moyenne_semestre:.2f} / 20")
    with c_res2:
        st.metric(label="Crédits ECTS validés", value=f"{total_ects_obtenus} / 30 ECTS")

    if moyenne_semestre >= 10.0:
        st.success("🏆 Semestre validé par compensation ou moyenne générale !")
    else:
        st.warning("⚠️ Moyenne sous la barre des 10/20.")

# --- MODULE 5 : N8N & AUTOMATISATIONS ---
elif mode == "n8n & Automatisations":
    st.subheader("Connexion d'Atlas aux applications externes via n8n")
    st.write("Exécutez des flux automatisés avec vos applications synchronisées dans votre instance n8n.")

    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("#### 📅 Google Calendar")
        if st.button("Planifier ma session de révision", use_container_width=True):
            res = call_n8n("create_calendar_event", {"matiere": matiere_selectionnee, "semestre": semestre_selectionne})
            if res:
                st.success("Événement ajouté à votre Google Calendar !")

    with c2:
        st.markdown("#### 📄 Google Docs / Drive")
        if st.button("Exporter la fiche sur Google Docs", use_container_width=True):
            res = call_n8n("export_google_doc", {"matiere": matiere_selectionnee, "cards": st.session_state.cards_data[semestre_selectionne][matiere_selectionnee]})
            if res:
                st.success("Document créé sur votre Google Drive !")

    with c3:
        st.markdown("#### 🎓 Moodle")
        if st.button("Synchro devoirs Moodle", use_container_width=True):
            res = call_n8n("sync_moodle", {"semestre": semestre_selectionne})
            if res:
                st.success("Devoirs récupérés depuis Moodle !")

# --- MODULE 6 : SAUVEGARDES ---
elif mode == "Sauvegardes":
    st.subheader("Gestion des données (Export / Import)")
    
    global_export = {
        "cards_data": st.session_state.cards_data,
        "notes_data": st.session_state.notes_data
    }
    
    json_str = json.dumps(global_export, indent=2, ensure_ascii=False)
    st.download_button(
        label="📥 Télécharger l'ensemble des données d'Atlas (JSON)",
        data=json_str,
        file_name="atlas_licence_gestion_data.json",
        mime="application/json"
    )

    st.divider()
    up = st.file_uploader("📤 Restaurer une sauvegarde (Fichier JSON)", type=["json"])
    if up:
        try:
            d = json.load(up)
            if "cards_data" in d:
                st.session_state.cards_data = d["cards_data"]
            if "notes_data" in d:
                st.session_state.notes_data = d["notes_data"]
            st.success("Toutes vos cartes et vos notes ont été restaurées !")
        except Exception as e:
            st.error(f"Erreur d'importation : {e}")
