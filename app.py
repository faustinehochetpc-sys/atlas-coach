import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Atlas - Coach", page_icon="🎓", layout="wide")

# Base de données intégrée en mémoire (évite tout crash de fichier JSON)
MATIERES = {
    # SEMESTRE 1
    "S1 - Intro aux sciences de gestion": "Bienvenue en Intro aux sciences de gestion (S1) !",
    "S1 - Hist. pensée & techniques managériales": "Bienvenue en Histoire de la pensée managériale (S1) !",
    "S1 - Introduction au droit": "Bienvenue en Introduction au droit (S1) !",
    "S1 - Théories éco & enjeux contemporains": "Bienvenue en Théories économiques (S1) !",
    "S1 - Micro-économie": "Bienvenue en Micro-économie (S1) !",
    "S1 - Expression écrite et orale": "Bienvenue en Expression écrite et orale (S1) !",
    "S1 - Fondamentaux de comptabilité": "Bienvenue en Fondamentaux de comptabilité (S1) !",
    "S1 - Informatique d'usage": "Bienvenue en Informatique d'usage (S1) !",
    "S1 - LV1 Anglais": "Welcome to English class (S1) !",
    "S1 - Accompagnement projet 1": "Bienvenue dans l'accompagnement de projet (S1) !",

    # SEMESTRE 2
    "S2 - Comptabilité générale": "Bienvenue en Comptabilité générale (S2) !",
    "S2 - Statistiques pour gestionnaires 1": "Bienvenue en Statistiques 1 (S2) !",
    "S2 - Droit commercial": "Bienvenue en Droit commercial (S2) !",
    "S2 - Marketing: histoire & réalités": "Bienvenue en Marketing (S2) !",
    "S2 - Négociation commerciale": "Bienvenue en Négociation commerciale (S2) !",
    "S2 - Géopolitique": "Bienvenue en Géopolitique (S2) !",
    "S2 - Sociologie de la consommation": "Bienvenue en Sociologie de la consommation (S2) !",
    "S2 - Informatique d'usage": "Bienvenue en Informatique d'usage (S2) !",
    "S2 - LV1 Anglais": "Welcome to English class (S2) !",

    # SEMESTRE 3
    "S3 - Marketing stratégique": "Bienvenue en Marketing stratégique (S3) !",
    "S3 - Techniques quantitatives de gestion": "Bienvenue en TQG (S3) !",
    "S3 - Statistiques pour gestionnaires 2": "Bienvenue en Statistiques 2 (S3) !",
    "S3 - Droit social": "Bienvenue en Droit social (S3) !",
    "S3 - Droit des sociétés": "Bienvenue en Droit des sociétés (S3) !",
    "S3 - Le manager face aux défis du numérique": "Bienvenue en Numérique & Environnement (S3) !",
    "S3 - Théorie des organisations": "Bienvenue en Théorie des organisations (S3) !",
    "S3 - International trades": "Bienvenue en International trades (S3) !",
    "S3 - Sales and negotiation": "Welcome to Sales and negotiation (S3) !",
    "S3 - LV1 Anglais": "Welcome to English class (S3) !",
    "S3 - Accompagnement projet 2": "Bienvenue dans l'accompagnement de projet (S3) !",

    # SEMESTRE 4
    "S4 - Comptabilité de gestion": "Bienvenue en Comptabilité de gestion (S4) !",
    "S4 - Marketing opérationnel": "Bienvenue en Marketing opérationnel (S4) !",
    "S4 - Droit fiscal": "Bienvenue en Droit fiscal (S4) !",
    "S4 - Mathématiques financières": "Bienvenue en Mathématiques financières (S4) !",
    "S4 - Technologies du web": "Bienvenue en Technologies du web (S4) !",
    "S4 - Projet": "Bienvenue dans l'espace Projet (S4) !",
    "S4 - Entrepreneuriat": "Bienvenue en Entrepreneuriat (S4) !",
    "S4 - Management de l'innovation": "Bienvenue en Management de l'innovation (S4) !",
    "S4 - Intro to international marketing": "Welcome to International Marketing (S4) !",
    "S4 - Management and environment": "Welcome to Management and Environment (S4) !",
    "S4 - LV1 Anglais": "Welcome to English class (S4) !",
    "S4 - Business game": "Bienvenue dans le Business Game (S4) !"
}

# Initialisation des messages dans la session
if "messages" not in st.session_state:
    st.session_state.messages = {}

# Barre latérale
with st.sidebar:
    st.title("🎓 Atlas Coach")
    selected_matiere = st.selectbox("Sélectionne ton cours :", list(MATIERES.keys()))
    
    if st.button("🔄 Réinitialiser la discussion"):
        st.session_state.messages[selected_matiere] = [
            {"role": "assistant", "content": MATIERES[selected_matiere]}
        ]
        st.rerun()

# Création du canal de discussion pour la matière si inexistant
if selected_matiere not in st.session_state.messages:
    st.session_state.messages[selected_matiere] = [
        {"role": "assistant", "content": MATIERES[selected_matiere]}
    ]

# Affichage principal
st.title(selected_matiere)

for msg in st.session_state.messages[selected_matiere]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = st.chat_input("Pose ta question ici...")

if prompt:
    # 1. Ajouter le message utilisateur
    st.session_state.messages[selected_matiere].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # 2. Générer la réponse
    with st.chat_message("assistant"):
        try:
            if "GEMINI_API_KEY" in st.secrets:
                genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                full_prompt = f"Tu es un coach académique. Réponds à l'étudiant pour son cours de {selected_matiere} : {prompt}"
                response = model.generate_content(full_prompt)
                answer = response.text
            else:
                answer = "❌ Clé API GEMINI_API_KEY introuvable dans les Secrets Streamlit."

            st.write(answer)
            st.session_state.messages[selected_matiere].append({"role": "assistant", "content": answer})

        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")
