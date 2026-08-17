import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import json
import os

st.set_page_config(page_title="Atlas Coach", page_icon="🎓", layout="wide")

DB_FILE = "chat_history.json"

# Fonctions de gestion de l'historique sur le disque
def load_history():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_history(history):
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Erreur de sauvegarde : {e}")

# DÉROULÉ PARCOURS MANAGEMENT (Licence Gestion - Semestres 1 à 4)
MATIERES = {
    # ESPACE GÉNÉRAL
    "🌐 Chat Général / Tous les cours": "Bienvenue dans ton espace global ! Pose ici tes questions transversales ou d'organisation générale.",

    # SEMESTRE 1
    "S1 - Introduction aux sciences de gestion": "Bienvenue en Introduction aux sciences de gestion !",
    "S1 - Histoire de la pensée et des techniques managériales": "Bienvenue en Histoire de la pensée et des techniques managériales !",
    "S1 - Introduction au droit": "Bienvenue en Introduction au droit !",
    "S1 - Théories économiques et enjeux contemporains": "Bienvenue en Théories économiques et enjeux contemporains !",
    "S1 - Micro-économie": "Bienvenue en Micro-économie !",
    "S1 - Expression écrite et orale": "Bienvenue en Expression écrite et orale !",
    "S1 - Fondamentaux de comptabilité": "Bienvenue en Fondamentaux de comptabilité !",
    "S1 - Informatique d'usage": "Bienvenue en Informatique d'usage !",
    "S1 - LV1 Anglais": "Welcome to English class (Semester 1) !",
    "S1 - Accompagnement à la réussite de mon projet 1": "Bienvenue dans le suivi de ton projet professionnel !",

    # SEMESTRE 2
    "S2 - Comptabilité générale": "Bienvenue en Comptabilité générale !",
    "S2 - Statistiques pour gestionnaires 1": "Bienvenue en Statistiques 1 !",
    "S2 - Droit commercial": "Bienvenue en Droit commercial !",
    "S2 - Marketing : histoire et réalités contemporaines": "Bienvenue en Marketing !",
    "S2 - Négociation commerciale": "Bienvenue en Négociation commerciale !",
    "S2 - Géopolitique": "Bienvenue en Géopolitique !",
    "S2 - Sociologie de la consommation": "Bienvenue en Sociologie de la consommation !",
    "S2 - Informatique d'usage": "Bienvenue en Informatique d'usage (S2) !",
    "S2 - LV1 Anglais": "Welcome to English class (Semester 2) !",

    # SEMESTRE 3
    "S3 - Marketing stratégique": "Bienvenue en Marketing stratégique !",
    "S3 - Techniques quantitatives de gestion": "Bienvenue en TQG !",
    "S3 - Statistiques pour gestionnaires 2": "Bienvenue en Statistiques 2 !",
    "S3 - Droit social": "Bienvenue en Droit social !",
    "S3 - Droit des sociétés": "Bienvenue en Droit des sociétés !",
    "S3 - Le manager face aux défis du numérique et de l'environnement": "Bienvenue en Numérique & Environnement !",
    "S3 - Théorie des organisations": "Bienvenue en Théorie des organisations !",
    "S3 - LV1 Anglais": "Welcome to English class (Semester 3) !",
    "S3 - Accompagnement à la réussite de mon projet 2": "Bienvenue dans le suivi de ton projet 2 !",

    # SEMESTRE 4
    "S4 - Comptabilité de gestion": "Bienvenue en Comptabilité de gestion !",
    "S4 - Marketing opérationnel": "Bienvenue en Marketing opérationnel !",
    "S4 - Droit fiscal": "Bienvenue en Droit fiscal !",
    "S4 - Mathématiques financières": "Bienvenue en Mathématiques financières !",
    "S4 - Technologies du web": "Bienvenue en Technologies du web !",
    "S4 - Projet": "Bienvenue dans l'espace Projet !",
    "S4 - Entrepreneuriat": "Bienvenue en Entrepreneuriat !",
    "S4 - Management de l'innovation": "Bienvenue en Management de l'innovation !",
    "S4 - LV1 Anglais": "Welcome to English class (Semester 4) !",
    "S4 - Business game": "Bienvenue dans le Business Game !"
}

# Extraction du texte des PDF/TXT téléversés
def extract_text_from_files(uploaded_files):
    extracted_text = ""
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith('.pdf'):
            reader = PdfReader(uploaded_file)
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
        elif uploaded_file.name.endswith('.txt'):
            extracted_text += uploaded_file.read().decode('utf-8') + "\n"
    return extracted_text

# Initialisation de l'historique permanent
if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_history()

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("🎓 Atlas Coach")
    
    selected_matiere = st.selectbox(
        "Sélectionne ton cours ou espace :", 
        list(MATIERES.keys())
    )
    
    st.markdown("---")
    st.header("📄 Fichiers du cours")
    uploaded_files = st.file_uploader(
        "Dépose tes cours (PDF, TXT) :",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        key=selected_matiere
    )
    
    st.markdown("---")
    if st.button("🗑️ Effacer cette discussion"):
        st.session_state.chat_history[selected_matiere] = [
            {"role": "assistant", "content": MATIERES[selected_matiere]}
        ]
        save_history(st.session_state.chat_history)
        st.rerun()

# Initialisation du canal si première visite
if selected_matiere not in st.session_state.chat_history:
    st.session_state.chat_history[selected_matiere] = [
        {"role": "assistant", "content": MATIERES[selected_matiere]}
    ]

# --- AFFICHAGE DU CHAT PRINCIPAL ---
st.title(selected_matiere)

for message in st.session_state.chat_history[selected_matiere]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input(f"Pose ta question sur {selected_matiere}...")

if user_input:
    st.session_state.chat_history[selected_matiere].append({"role": "user", "content": user_input})
    save_history(st.session_state.chat_history)
    
    with st.chat_message("user"):
        st.write(user_input)
        
    with st.chat_message("assistant"):
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            error_msg = "⚠️ La clé API `GEMINI_API_KEY` n'est pas configurée dans `.streamlit/secrets.toml`."
            st.warning(error_msg)
            st.session_state.chat_history[selected_matiere].append({"role": "assistant", "content": error_msg})
            save_history(st.session_state.chat_history)
        else:
            try:
                genai.configure(api_key=api_key)
                
                # Contextualisation selon l'espace choisi
                if selected_matiere == "🌐 Chat Général / Tous les cours":
                    system_prompt = "Tu es Atlas, un coach pédagogique personnel en Licence de Gestion (Parcours Management). Tu aides l'étudiant à s'organiser, réviser de façon transversale et préparer sa rentrée."
                else:
                    system_prompt = f"Tu es Atlas, un coach expert de la matière '{selected_matiere}' en Licence de Gestion. Donne des explications claires, structurées et adaptées au niveau universitaire."
                
                # Prise en compte des documents déposés
                context_text = ""
                if uploaded_files:
                    files_text = extract_text_from_files(uploaded_files)
                    if files_text:
                        context_text = f"\n\nCONTENU DES COURS FOURNIS :\n{files_text[:4000]}"
                
                full_prompt = f"{system_prompt}{context_text}\n\nQuestion de l'élève : {user_input}"
                
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(full_prompt)
                
                st.write(response.text)
                st.session_state.chat_history[selected_matiere].append({"role": "assistant", "content": response.text})
                save_history(st.session_state.chat_history)
                
            except Exception as e:
                st.error(f"Erreur lors de la génération : {e}")
