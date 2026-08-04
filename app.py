import streamlit as st
from google import genai
from google.genai import types

# Titre principal et configuration
st.set_page_config(page_title="Atlas - Coach", page_icon="🎓")
st.title("🎓 Atlas - Ton Coach Personnel")

# --- INITIALISATION DE GEMINI ---
if "chat" not in st.session_state:
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    system_instruction = "Tu es Atlas, un coach pédagogique bienveillant et structuré."

    st.session_state.chat = client.chats.create(
        model="gemini-1.5-flash",
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

    if uploaded_files:
        if st.button("Envoyer les documents à Atlas"):
            for uploaded_file in uploaded_files:
                bytes_data = uploaded_file.read()
                prompt_doc = f"Voici le document nommé '{uploaded_file.name}' :\n\n"

                try:
                    contenu_texte = bytes_data.decode("utf-8")
                    prompt_doc += contenu_texte
                except UnicodeDecodeError:
                    prompt_doc += f"[Fichier binaire/PDF chargé de {len(bytes_data)} octets]"

                response = st.session_state.chat.send_message(prompt_doc)
                st.session_state.messages.append({
                    "role": "system",
                    "content": f"📄 Document chargé : **{uploaded_file.name}**"
                })
            st.success("Documents intégrés à la mémoire d'Atlas !")

# --- AFFICHAGE DU CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"] if msg["role"] != "system" else "assistant"):
        st.markdown(msg["content"])

# Zone de saisie utilisateur
if prompt := st.chat_input("Pose une question à Atlas..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    response = st.session_state.chat.send_message(prompt)

    with st.chat_message("assistant"):
        st.markdown(response.text)
    st.session_state.messages.append({"role": "assistant", "content": response.text})
