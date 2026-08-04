import streamlit as st
import google.generativeai as genai

# Configuration de la page
st.set_page_config(page_title="Atlas - Coach", page_icon="🎓")
st.title("🎓 Atlas - Ton Coach Personnel")

# --- HISTORIQUE DE CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.header("📚 Tes cours & notes")
    uploaded_files = st.file_uploader(
        "Dépose tes fichiers ici (PDF, TXT...) :",
        accept_multiple_files=True
    )

# --- AFFICHAGE DE L'HISTORIQUE ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ENTRÉE UTILISATEUR & RÉPONSE ---
if prompt := st.chat_input("Pose une question à Atlas..."):
    # 1. Afficher la question
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Générer la réponse
    with st.chat_message("assistant"):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            
            # Utilisation du nom exacte issu de ta liste (ligne 10)
            model = genai.GenerativeModel(
                model_name="gemini-flash-latest",
                system_instruction="Tu es Atlas, un coach pédagogique bienveillant et structuré."
            )
            
            response = model.generate_content(prompt)
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"Erreur : {e}")
