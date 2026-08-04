import streamlit as st
from google import genai
from google.genai.errors import APIError

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
            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"Une erreur est survenue : {e}")
