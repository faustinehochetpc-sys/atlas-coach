import json
import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from google import genai
from pypdf import PdfReader

# Chargement automatique des variables d'environnement (.env)
load_dotenv()

# ============================================================
# CONFIGURATION INITIALE
# ============================================================

st.set_page_config(
    page_title="Atlas — beau-gosse",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = Path("atlas_data.json")
GEMINI_MODEL = "gemini-3.5-flash"
MAX_CONTEXT_CHARS = 100000

MATIERES_PAR_SEMESTRE = {
    "Tous les semestres": ["🌐 Chat Général / Tous les cours"],
    "Semestre 1 (S1)": [
        "🌐 Tous les cours S1",
        "S1 - Introduction aux sciences de gestion",
        "S1 - Histoire de la pensée et des techniques managériales",
        "S1 - Introduction au droit",
        "S1 - Théories économiques et enjeux contemporains",
        "S1 - Micro-économie",
        "S1 - Expression écrite et orale",
        "S1 - Fondamentaux de comptabilité",
        "S1 - Informatique d'usage",
        "S1 - LV1 Anglais",
        "S1 - Accompagnement à la réussite de mon projet 1",
    ],
    "Semestre 2 (S2)": [
        "🌐 Tous les cours S2",
        "S2 - Comptabilité générale",
        "S2 - Statistiques pour gestionnaires 1",
        "S2 - Droit commercial",
        "S2 - Marketing : histoire et réalités contemporaines",
        "S2 - Négociation commerciale",
        "S2 - Géopolitique",
        "S2 - Sociologie de la consommation",
        "S2 - Informatique d'usage",
        "S2 - LV1 Anglais",
    ],
    "Semestre 3 (S3)": [
        "🌐 Tous les cours S3",
        "S3 - Marketing stratégique",
        "S3 - Techniques quantitatives de gestion",
        "S3 - Mathématiques financières",
        "S3 - Droit social",
        "S3 - Droit des sociétés",
        "S3 - Le manager face aux défis du numérique et de l'environnement",
        "S3 - Théorie des organisations",
        "S3 - LV1 Anglais",
        "S3 - Accompagnement à la réussite de mon projet 2",
    ],
    "Semestre 4 (S4)": [
        "🌐 Tous les cours S4",
        "S4 - Comptabilité de gestion",
        "S4 - Marketing opérationnel",
        "S4 - Droit fiscal",
        "S4 - Statistiques pour gestionnaires 2",
        "S4 - Technologies du web",
        "S4 - Projet",
        "S4 - Entrepreneuriat",
        "S4 - Management de l'innovation",
        "S4 - LV1 Anglais",
        "S4 - Business game",
    ],
}

LISTE_MATIERES = [m for liste in MATIERES_PAR_SEMESTRE.values() for m in liste]

# ============================================================
# GESTION DES PREFÉRENCES ET HISTORIQUE PRIVÉ
# ============================================================

def load_data():
    if DATA_FILE.exists():
        try:
            with DATA_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}
    else:
        data = {}

    data.setdefault("obsidian_vault_path", "")
    data.setdefault("notes_generales", "")
    data.setdefault("notes_specifiques", {})

    for matiere in LISTE_MATIERES:
        data["notes_specifiques"].setdefault(matiere, "")

    return data

def save_data(data):
    try:
        with DATA_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Erreur de sauvegarde : {e}")

if "data" not in st.session_state:
    st.session_state.data = load_data()

# Historique des chats propre à la session utilisateur (non partagé)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

# ============================================================
# EXTRACTION DU CONTENU OBSIDIAN (MARKDOWN ET PDF)
# ============================================================

def parse_obsidian_vault(vault_path):
    if not vault_path or not os.path.exists(vault_path):
        return ""
    extracted = ""
    for root, _, files in os.walk(vault_path):
        for file in files:
            file_path = os.path.join(root, file)

            if file.lower().endswith(".md"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        extracted += f"\n--- Note Obsidian (.md): {file} ---\n{f.read()}\n"
                except Exception:
                    pass

            elif file.lower().endswith(".pdf"):
                try:
                    reader = PdfReader(file_path)
                    pdf_text = ""
                    for page in reader.pages:
                        text = page.extract_text()
                        if text:
                            pdf_text += text + "\n"
                    if pdf_text:
                        extracted += f"\n--- Fichier PDF: {file} ---\n{pdf_text}\n"
                except Exception:
                    pass

    return extracted

# ============================================================
# MOTEUR GEMINI
# ============================================================

def build_system_instruction(selected_matiere, context, notes_gen, notes_mat):
    base_role = f"Tu es Atlas, un coach pédagogique expert pour la matière {selected_matiere}."
    
    ctx_block = f"\n\nCONTENU DE TES COURS OBSIDIAN :\n{context[:MAX_CONTEXT_CHARS]}" if context else "\n\nAucun cours Obsidian chargé."
    notes_block = f"\n\nNOTES GÉNÉRALES :\n{notes_gen}\nNOTES SPÉCIFIQUES :\n{notes_mat}"

    return f"""{base_role}

Ton rôle est d'aider l'étudiant à réviser, comprendre et réussir ses examens.
- Base tes réponses en priorité sur le contenu Obsidian fourni ci-dessous.
- Si le contenu Obsidian est insuffisant pour répondre, complète avec tes connaissances de niveau Licence en le précisant.
- Sois clair, concis et pédagogique.{notes_block}{ctx_block}"""

def query_gemini(api_key, selected_matiere, messages, prompt, context, notes_gen, notes_mat):
    client = genai.Client(api_key=api_key.strip())
    system_instruction = build_system_instruction(selected_matiere, context, notes_gen, notes_mat)
    
    contents = []
    for idx, msg in enumerate(messages):
        if idx == 0 and msg["role"] == "assistant":
            continue
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    
    contents.append({"role": "user", "parts": [{"text": prompt}]})

    response_stream = client.models.generate_content_stream(
        model=GEMINI_MODEL,
        contents=contents,
        config={"system_instruction": system_instruction, "temperature": 0.5},
    )
    for chunk in response_stream:
        if chunk.text:
            yield chunk.text

# ============================================================
# INTERFACE SIDEBAR
# ============================================================

env_api_key = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")

with st.sidebar:
    st.title("🎓 Atlas")

    # --- CLÉ API SÉCURISÉE ---
    st.subheader("🔑 Clé API Gemini")
    
    if env_api_key:
        st.success("🔒 Clé API chargée en toute sécurité.")
        active_key = env_api_key
    else:
        api_key_input = st.text_input(
            "Colle ta clé API Gemini :",
            type="password",
            value=st.session_state.get("user_gemini_key", ""),
            placeholder="AIzaSy...",
        )
        if api_key_input:
            st.session_state["user_gemini_key"] = api_key_input.strip()
        active_key = st.session_state.get("user_gemini_key", "")

    st.divider()

    # --- SÉLECTION MATIÈRE ---
    semestre = st.selectbox("📚 Semestre", list(MATIERES_PAR_SEMESTRE.keys()))
    selected_matiere = st.selectbox("Matière", MATIERES_PAR_SEMESTRE[semestre])

    st.divider()

    # --- OBSIDIAN ---
    with st.expander("📂 Dossier Obsidian", expanded=True):
        obs_path = st.text_input(
            "Chemin absolu du dossier :",
            value=st.session_state.data.get("obsidian_vault_path", ""),
            placeholder="/Users/nom/Documents/MonVault"
        )
        if st.button("Enregistrer le chemin", use_container_width=True):
            st.session_state.data["obsidian_vault_path"] = obs_path
            save_data(st.session_state.data)
            st.success("Chemin mis à jour !")

    # --- NOTES ---
    with st.expander("📝 Bloc-notes"):
        st.markdown("**Notes Générales**")
        gen_notes = st.text_area("Objectifs, planning...", value=st.session_state.data["notes_generales"], height=80)
        if gen_notes != st.session_state.data["notes_generales"]:
            st.session_state.data["notes_generales"] = gen_notes
            save_data(st.session_state.data)

        st.markdown(f"**Notes pour {selected_matiere}**")
        curr_notes = st.session_state.data["notes_specifiques"].get(selected_matiere, "")
        spec_notes = st.text_area("Points à revoir...", value=curr_notes, height=80)
        if spec_notes != curr_notes:
            st.session_state.data["notes_specifiques"][selected_matiere] = spec_notes
            save_data(st.session_state.data)

    st.divider()
    if st.button("🔄 Effacer cette discussion", use_container_width=True):
        st.session_state.chat_history[selected_matiere] = [
            {"role": "assistant", "content": f"Espace réinitialisé pour {selected_matiere}."}
        ]
        st.rerun()

# Initialisation du chat pour la matière sélectionnée si absent
if selected_matiere not in st.session_state.chat_history:
    st.session_state.chat_history[selected_matiere] = [
        {"role": "assistant", "content": f"Espace de travail Atlas prêt pour {selected_matiere} !"}
    ]

# ============================================================
# ZONE PRINCIPALE
# ============================================================

st.title(f"📌 {selected_matiere}")

obsidian_context = parse_obsidian_vault(st.session_state.data.get("obsidian_vault_path", ""))

if obsidian_context:
    st.caption("✅ Cours Obsidian intégrés au contexte.")
else:
    st.caption("⚠️ Aucun dossier Obsidian trouvé. Indiquez le chemin dans le panneau latéral.")

# --- OUTILS GÉNÉRATEURS RAPIDES ---
st.subheader("⚡ Outils de révision rapide")
col1, col2, col3, col4 = st.columns(4)

prompt_generator = None

with col1:
    if st.button("❓ Générer un QCM", use_container_width=True):
        prompt_generator = "Génère un QCM de 5 questions basé sur mes cours d'Obsidian avec la correction détaillée à la fin."

with col2:
    if st.button("✏️ Exercice d'application", use_container_width=True):
        prompt_generator = "Donne-moi un exercice d'application concis basé sur mon cours Obsidian, puis propose-moi de donner ma réponse avant de me corriger."

with col3:
    if st.button("💡 Fiche de synthèse", use_container_width=True):
        prompt_generator = "Fais une fiche de synthèse ultra-structurée des concepts clés présents dans mes notes Obsidian pour cette matière."

with col4:
    if st.button("🟨 Flashcards Anki", use_container_width=True):
        prompt_generator = (
            "Génère 10 flashcards basées sur le cours Obsidian sous le format texte strict prêt pour Anki :\n"
            "Question;Réponse\n"
            "Mets l'ensemble des cartes dans un bloc de code pour que je puisse tout copier d'un coup."
        )

# --- GESTION DU CHAT ISOLÉ PAR UTILISATEUR ---
chat_history = st.session_state.chat_history[selected_matiere]

for message in chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Pose une question ou demande des révisions...")
final_prompt = prompt_generator if prompt_generator else user_input

if final_prompt:
    if not active_key:
        st.error("⚠️ Veuillez coller votre clé API Gemini dans le panneau latéral à gauche.")
    else:
        st.chat_message("user").markdown(final_prompt)
        chat_history.append({"role": "user", "content": final_prompt})

        with st.chat_message("assistant"):
            try:
                response_stream = query_gemini(
                    api_key=active_key,
                    selected_matiere=selected_matiere,
                    messages=chat_history[:-1],
                    prompt=final_prompt,
                    context=obsidian_context,
                    notes_gen=st.session_state.data["notes_generales"],
                    notes_mat=st.session_state.data["notes_specifiques"].get(selected_matiere, "")
                )
                full_response = st.write_stream(response_stream)
                chat_history.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Erreur API Gemini : {e}")
