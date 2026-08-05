import streamlit as st
import google.generativeai as genai
import json
import os

# --- CONFIGURATION FICHIERS DE STOCKAGE ---
DATA_FILE = "atlas_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "profile": {
            "objectif": "Réussir mes examens et booster ma productivité",
            "style": "Explications simples avec exemples concrets"
        },
        "matieres": {
            "🐍 Python": [{"role": "assistant", "content": "Bienvenue dans ton espace Python ! Quelle notion souhaites-tu travailler aujourd'hui ?"}],
            "🗄️ SQL": [{"role": "assistant", "content": "Bienvenue dans ton espace SQL ! Pose-moi tes questions sur les requêtes ou les bases de données."}],
            "⚖️ Droit": [{"role": "assistant", "content": "Bienvenue dans ton espace Droit ! Un cas pratique ou une fiche de cours à réviser ?"}],
            "📅 Planning & Organisation": [{"role": "assistant", "content": "Prêt pour structurer ta séance de travail ? Dis-moi combien de temps tu as."}]
        }
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

st.set_page_config(page_title="Atlas - Coach", page_icon="🎓", layout="wide")

if "data" not in st.session_state:
    st.session_state.data = load_data()

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("🎓 Atlas Coach")
    st.header("📚 Tes Cours & Matières")
    
    list_matieres = list(st.session_state.data["matieres"].keys())
    selected_matiere = st.selectbox("Sélectionne ton cours :", list_matieres)
    
    with st.popover("➕ Ajouter une matière"):
        new_mat_name = st.text_input("Nom de la matière (ex: 📖 Histoire) :")
        if st.button("Créer la matière") and new_mat_name:
            if new_mat_name not in st.session_state.data["matieres"]:
                st.session_state.data["matieres"][new_mat_name] = [
                    {"role": "assistant", "content": f"Espace de travail créé pour {new_mat_name} !"}
                ]
                save_data(st.session_state.data)
                st.rerun()

    st.markdown("---")
    if st.button("🔄 Réinitialiser ce cours"):
        st.session_state.data["matieres"][selected_matiere] = [
            {"role": "assistant", "content": f"Discussion réinitialisée pour {selected_matiere}."}
        ]
        save_data(st.session_state.data)
        st.rerun()

    st.markdown("---")
    st.header("📄 Fichiers du cours")
    uploaded_files = st.file_uploader(
        "Dépose tes cours (PDF, TXT) :",
        accept_multiple_files=True,
        key=selected_matiere
    )

    st.markdown("---")
    with st.expander("⚙️ Profil & Préférences"):
        prof_obj = st.text_input("Objectif :", value=st.session_state.data["profile"].get("objectif", ""))
        prof_style = st.selectbox(
            "Style de réponse :",
            ["Explications simples avec exemples concrets", "Synthétique et direct", "Détaillé et académique"],
            index=0
        )
        if st.button("💾 Sauvegarder profil"):
            st.session_state.data["profile"]["objectif"] = prof_obj
            st.session_state.data["profile"]["style"] = prof_style
            save_data(st.session_state.data)
            st.success("Profil enregistré !")

# --- CONTENU PRINCIPAL ---
st.title(f"{selected_matiere}")
st.caption(f"Espace de travail dédié • {st.session_state.data['profile']['objectif']}")

current_messages = st.session_state.data["matieres"][selected_matiere]

for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- ENTRÉE UTILISATEUR ---
st.subheader("🎙️ Parler à Atlas")
audio_input = st.audio_input("Enregistre ton message vocal")
prompt = st.chat_input(f"Pose ta question pour {selected_matiere}...")

user_submitted = False
contents_payload = []

if audio_input is not None:
    audio_bytes = audio_input.read()
    current_messages.append({"role": "user", "content": "🎙️ *[Message vocal envoyé]*"})
    contents_payload.append({
        "mime_type": audio_input.type,
        "data": audio_bytes
    })
    user_submitted = True

elif prompt:
    current_messages.append({"role": "user", "content": prompt})
    contents_payload.append(prompt)
    user_submitted = True

if user_submitted:
    with st.chat_message("user"):
        st.markdown(current_messages[-1]["content"])

    with st.chat_message("assistant"):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            
            prof = st.session_state.data["profile"]
            system_instruction = (
                "Tu es Atlas, un coach pédagogique personnel, bienveillant et super structuré.\n"
                f"CONTEXTE ACTUEL :\n"
                f"- Matière étudiée : {selected_matiere}\n"
                f"- Objectif de l'élève : {prof.get('objectif')}\n"
                f"- Style d'explication souhaité : {prof.get('style')}\n\n"
                f"Adapte toutes tes réponses spécifiquement au domaine de {selected_matiere}."
            )

            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=system_instruction
            )
            
            response = model.generate_content(contents_payload)
            
            st.markdown(response.text)
            current_messages.append({"role": "assistant", "content": response.text})
            
            save_data(st.session_state.data)
            
        except Exception as e:
            st.error(f"Erreur : {e}")
