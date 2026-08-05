import streamlit as st
import google.generativeai as genai

# Configuration de l'application
st.set_page_config(page_title="Atlas Coach", page_icon="🎓", layout="wide")

# Liste des matières organisées par semestre
MATIERES = {
    # SEMESTRE 1
    "S1 - Intro aux sciences de gestion": "Bienvenue en Intro aux sciences de gestion !",
    "S1 - Hist. pensée & techniques managériales": "Bienvenue en Histoire de la pensée managériale !",
    "S1 - Introduction au droit": "Bienvenue en Introduction au droit !",
    "S1 - Théories éco & enjeux contemporains": "Bienvenue en Théories économiques !",
    "S1 - Micro-économie": "Bienvenue en Micro-économie !",
    "S1 - Expression écrite et orale": "Bienvenue en Expression écrite et orale !",
    "S1 - Fondamentaux de comptabilité": "Bienvenue en Fondamentaux de comptabilité !",
    "S1 - Informatique d'usage": "Bienvenue en Informatique d'usage !",
    "S1 - LV1 Anglais": "Welcome to English class !",
    "S1 - Accompagnement projet 1": "Bienvenue dans l'accompagnement de projet !",

    # SEMESTRE 2
    "S2 - Comptabilité générale": "Bienvenue en Comptabilité générale !",
    "S2 - Statistiques pour gestionnaires 1": "Bienvenue en Statistiques 1 !",
    "S2 - Droit commercial": "Bienvenue en Droit commercial !",
    "S2 - Marketing: histoire & réalités": "Bienvenue en Marketing !",
    "S2 - Négociation commerciale": "Bienvenue en Négociation commerciale !",
    "S2 - Géopolitique": "Bienvenue en Géopolitique !",
    "S2 - Sociologie de la consommation": "Bienvenue en Sociologie de la consommation !",
    "S2 - Informatique d'usage": "Bienvenue en Informatique d'usage !",
    "S2 - LV1 Anglais": "Welcome to English class !",

    # SEMESTRE 3
    "S3 - Marketing stratégique": "Bienvenue en Marketing stratégique !",
    "S3 - Techniques quantitatives de gestion": "Bienvenue en TQG !",
    "S3 - Statistiques pour gestionnaires 2": "Bienvenue en Statistiques 2 !",
    "S3 - Droit social": "Bienvenue en Droit social !",
    "S3 - Droit des sociétés": "Bienvenue en Droit des sociétés !",
    "S3 - Le manager face aux défis du numérique": "Bienvenue en Numérique & Environnement !",
    "S3 - Théorie des organisations": "Bienvenue en Théorie des organisations !",
    "S3 - International trades": "Bienvenue en International trades !",
    "S3 - Sales and negotiation": "Welcome to Sales and negotiation !",
    "S3 - LV1 Anglais": "Welcome to English class !",
    "S3 - Accompagnement projet 2": "Bienvenue dans l'accompagnement de projet !",

    # SEMESTRE 4
    "S4 - Comptabilité de gestion": "Bienvenue en Comptabilité de gestion !",
    "S4 - Marketing opérationnel": "Bienvenue en Marketing opérationnel !",
    "S4 - Droit fiscal": "Bienvenue en Droit fiscal !",
    "S4 - Mathématiques financières": "Bienvenue en Mathématiques financières !",
    "S4 - Technologies du web": "Bienvenue en Technologies du web !",
    "S4 - Projet": "Bienvenue dans l'espace Projet !",
    "S4 - Entrepreneuriat": "Bienvenue en Entrepreneuriat !",
    "S4 - Management de l'innovation": "Bienvenue en Management de l'innovation !",
    "S4 - Intro to international marketing": "Welcome to International Marketing !",
    "S4 - Management and environment": "Welcome to Management and Environment !",
    "S4 - LV1 Anglais": "Welcome to English class !",
    "S4 - Business game": "Bienvenue dans le Business Game !"
}

# Initialisation de la mémoire de l'application
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

# Menu latéral
with st.sidebar:
    st.title("🎓 Atlas Coach")
    selected_matiere = st.selectbox("Sélectionne ton cours :", list(MATIERES.keys()))
    
    if st.button("🗑️ Effacer cette discussion"):
        st.session_state.chat_history[selected_matiere] = [
            {"role": "assistant", "content": MATIERES[selected_matiere]}
        ]
        st.rerun()

# Création du fil de discussion de la matière si inexistant
if selected_matiere not in st.session_state.chat_history:
    st.session_state.chat_history[selected_matiere] = [
        {"role": "assistant", "content": MATIERES[selected_matiere]}
    ]

# Zone d'affichage
st.title(selected_matiere)

for message in st.session_state.chat_history[selected_matiere]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Entrée utilisateur
user_input = st.chat_input("Pose ta question sur ce cours...")

if user_input:
    # Sauvegarde et affichage du message utilisateur
    st.session_state.chat_history[selected_matiere].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Réponse de l'assistant
    with st.chat_message("assistant"):
        api_key = st.secrets.get("GEMINI_API_KEY")
        
        if not api_key:
            error_msg = "⚠️ La clé API `GEMINI_API_KEY` n'est pas configurée dans les Secrets de Streamlit."
            st.warning(error_msg)
            st.session_state.chat_history[selected_matiere].append({"role": "assistant", "content": error_msg})
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                
                prompt_contextuel = (
                    f"Tu es un tuteur universitaire pédagogique et bienveillant. "
                    f"Aide l'étudiant spécifiquement pour le cours de '{selected_matiere}'. "
                    f"Question : {user_input}"
                )
                
                response = model.generate_content(prompt_contextuel)
                reply = response.text
                
                st.write(reply)
                st.session_state.chat_history[selected_matiere].append({"role": "assistant", "content": reply})
                
            except Exception as e:
                error_msg = f"Erreur lors de la réponse : {e}"
                st.error(error_msg)
                st.session_state.chat_history[selected_matiere].append({"role": "assistant", "content": error_msg})
