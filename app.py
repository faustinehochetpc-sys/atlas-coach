import streamlit as st
import google.generativeai as genai
import json
import os

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Atlas - Coach", page_icon="🎓", layout="wide")

DATA_FILE = "atlas_data.json"

def get_default_data():
    return {
        "profile": {
            "objectif": "Réussir ma Licence de Gestion",
            "style": "Explications simples avec exemples concrets"
        },
        "matieres": {
            # SEMESTRE 1
            "S1 - 🏢 Intro aux sciences de gestion": [{"role": "assistant", "content": "Bienvenue dans le cours d'Introduction aux sciences de gestion (S1) !"}],
            "S1 - 📜 Hist. pensée & techniques managériales": [{"role": "assistant", "content": "Bienvenue dans le cours d'Histoire de la pensée managériale (S1) !"}],
            "S1 - ⚖️ Introduction au droit": [{"role": "assistant", "content": "Bienvenue en Introduction au droit (S1) !"}],
            "S1 - 📈 Théories éco & enjeux contemporains": [{"role": "assistant", "content": "Bienvenue en Théories économiques (S1) !"}],
            "S1 - 📊 Micro-économie": [{"role": "assistant", "content": "Bienvenue en Micro-économie (S1) !"}],
            "S1 - ✍️ Expression écrite et orale": [{"role": "assistant", "content": "Bienvenue en Expression écrite et orale (S1) !"}],
            "S1 - 🧮 Fondamentaux de comptabilité": [{"role": "assistant", "content": "Bienvenue en Fondamentaux de comptabilité (S1) !"}],
            "S1 - 💻 Informatique d'usage": [{"role": "assistant", "content": "Bienvenue en Informatique d'usage (S1) !"}],
            "S1 - 🇬🇧 LV1 Anglais": [{"role": "assistant", "content": "Welcome to English class (S1) !"}],
            "S1 - 🎯 Accompagnement projet 1": [{"role": "assistant", "content": "Bienvenue dans ton espace d'accompagnement de projet (S1) !"}],

            # SEMESTRE 2
            "S2 - 🧮 Comptabilité générale": [{"role": "assistant", "content": "Bienvenue en Comptabilité générale (S2) !"}],
            "S2 - 📉 Statistiques pour gestionnaires 1": [{"role": "assistant", "content": "Bienvenue en Statistiques 1 (S2) !"}],
            "S2 - ⚖️ Droit commercial": [{"role": "assistant", "content": "Bienvenue en Droit commercial (S2) !"}],
            "S2 - 📣 Marketing: histoire & réalités": [{"role": "assistant", "content": "Bienvenue en Marketing (S2) !"}],
            "S2 - 🤝 Négociation commerciale": [{"role": "assistant", "content": "Bienvenue en Négociation commerciale (S2) !"}],
            "S2 - 🌍 Géopolitique": [{"role": "assistant", "content": "Bienvenue en Géopolitique (S2) !"}],
            "S2 - 👥 Sociologie de la consommation": [{"role": "assistant", "content": "Bienvenue en Sociologie de la consommation (S2) !"}],
            "S2 - 💻 Informatique d'usage": [{"role": "assistant", "content": "Bienvenue en Informatique d'usage (S2) !"}],
            "S2 - 🇬🇧 LV1 Anglais": [{"role": "assistant", "content": "Welcome to English class (S2) !"}],

            # SEMESTRE 3
            "S3 - 🎯 Marketing stratégique": [{"role": "assistant", "content": "Bienvenue en Marketing stratégique (S3) !"}],
            "S3 - 📐 Techniques quantitatives de gestion": [{"role": "assistant", "content": "Bienvenue en TQG (S3) !"}],
            "S3 - 📉 Statistiques pour gestionnaires 2": [{"role": "assistant", "content": "Bienvenue en Statistiques 2 (S3) !"}],
            "S3 - ⚖️ Droit social": [{"role": "assistant", "content": "Bienvenue en Droit social (S3) !"}],
            "S3 - ⚖️ Droit des sociétés": [{"role": "assistant", "content": "Bienvenue en Droit des sociétés (S3) !"}],
            "S3 - 🌐 Le manager face aux défis du numérique": [{"role": "assistant", "content": "Bienvenue en Numérique & Environnement (S3) !"}],
            "S3 - 🏗️ Théorie des organisations": [{"role": "assistant", "content": "Bienvenue en Théorie des organisations (S3) !"}],
            "S3 - 🚢 International trades": [{"role": "assistant", "content": "Bienvenue en International trades (S3) !"}],
            "S3 - 🗣️ Sales and negotiation": [{"role": "assistant", "content": "Welcome to Sales and negotiation (S3) !"}],
            "S3 - 🇬🇧 LV1 Anglais": [{"role": "assistant", "content": "Welcome to English class (S3) !"}],
            "S3 - 🎯 Accompagnement projet 2": [{"role": "assistant", "content": "Bienvenue dans ton espace d'accompagnement de projet (S3) !"}],

            # SEMESTRE 4
            "S4 - 📊 Comptabilité de gestion": [{"role": "assistant", "content": "Bienvenue en Comptabilité de gestion (S4) !"}],
            "S4 - 📢 Marketing opérationnel": [{"role": "assistant", "content": "Bienvenue en Marketing opérationnel (S4) !"}],
            "S4 - 🏛️ Droit fiscal": [{"role": "assistant", "content": "Bienvenue en Droit fiscal (S4) !"}],
            "S4 - 🔢 Mathématiques financières": [{"role": "assistant", "content": "Bienvenue en Mathématiques financières (S4) !"}],
            "S4 - 🌐 Technologies du web": [{"role": "assistant", "content": "Bienvenue en Technologies du web (S4) !"}],
            "S4 - 📁 Projet": [{"role": "assistant", "content": "Bienvenue dans ton espace Projet (S4) !"}],
            "S4 - 🚀 Entrepreneuriat": [{"role": "assistant", "content": "Bienvenue en Entrepreneuriat (S4) !"}],
            "S4 - 💡 Management de l'innovation": [{"role": "assistant", "content": "Bienvenue en Management de l'innovation (S4) !"}],
            "S4 - 🌏 Intro to international marketing": [{"role": "assistant", "content": "Welcome to International Marketing (S4) !"}],
            "S4 - 🍃 Management and environment": [{"role": "assistant", "content": "Welcome to Management and Environment (S4) !"}],
            "S4 - 🇬🇧 LV1 Anglais": [{"role": "assistant", "content": "Welcome to English class (S4) !"}],
            "S4 - 🎮 Business game": [{"role": "assistant", "content": "Bienvenue dans le Business Game (S4) !"}]
        }
    }

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return get_default_data()

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if "data" not in st.session_state:
    st.session_state.data = load_data()

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("🎓 Atlas Coach")
    st.header("📚 Programme Licence")
    
    matieres_keys = list(st.session_state.data["matieres"].keys())
    selected_matiere = st.selectbox("Sélectionne ton cours :", matieres_keys)
    
    st.markdown("---")
    if st.button("🔄 Réinitialiser la discussion"):
        st.session_state.data["matieres"][selected_matiere] = [
            {"role": "assistant", "content": f"Discussion réinitialisée pour {selected_matiere}."}
        ]
        save_data(st.session_state.data)
        st.rerun()

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
            st.success("Profil mis à jour !")

# --- CONTENU PRINCIPAL ---
st.title(selected_matiere)
st.caption(f"Objectif : {st.session_state.data['profile']['objectif']}")

current_messages = st.session_state.data["matieres"].get(selected_matiere, [])

for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrée textuelle uniquement
prompt = st.chat_input(f"Pose ta question pour {selected_matiere}...")

if prompt:
    current_messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
            
            prof = st.session_state.data["profile"]
            system_instruction = (
                f"Tu es Atlas, un coach pédagogique personnel, bienveillant et structuré.\n"
                f"CONTEXTE ACTUEL :\n"
                f"- Matière : {selected_matiere}\n"
                f"- Objectif : {prof.get('objectif')}\n"
                f"- Style : {prof.get('style')}\n\n"
                f"Adapte tes réponses spécifiquement au cours de {selected_matiere}."
            )

            model = genai.GenerativeModel(
                model_name="models/gemini-1.5-flash",
                system_instruction=system_instruction
            )
            
            # Formatage de l'historique pour Gemini
            history_payload = []
            for msg in current_messages:
                role = "user" if msg["role"] == "user" else "model"
                history_payload.append({"role": role, "parts": [msg["content"]]})

            response = model.generate_content(history_payload)
            
            st.markdown(response.text)
            current_messages.append({"role": "assistant", "content": response.text})
            save_data(st.session_state.data)
            
        except Exception as e:
            st.error(f"Erreur de connexion à l'IA : {e}")
