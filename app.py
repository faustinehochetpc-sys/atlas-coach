import streamlit as st
from google import genai
from google.genai import types

# Titre principal et configuration
st.set_page_config(page_title="Atlas - Coach", page_icon="🎓")
st.title("🎓 Atlas - Ton Coach Personnel")

# --- INITIALISATION DE GEMINI ---
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

if "chat" not in st.session_state:
    system_instruction = "Tu es Atlas, un coach pédagogique bienveillant et structuré."
    st.session_state.chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
        )
    )

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- BARRE LATÉRALE : Import des cours ---
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

# --- ENTÉRÉE UTILISATEUR & RÉPONSE ---
if prompt := st.chat_input("Pose une question à Atlas..."):
    # Afficher le message de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Réponse d'Atlas
    with st.chat_message("assistant"):
        response = st.session_state.chat.send_message(prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
