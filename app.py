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
# CONFIGURATION ET STYLE DYNAMIQUE (CLAIR / SOMBRE)
# ============================================================

st.set_page_config(
    page_title="Atlas — Assistant Étudiant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    /* Adaptation dynamique selon le thème (Clair/Sombre) */
    .stApp { 
        background-color: var(--background-color); 
        color: var(--text-color);
    }
    
    /* Cartes et conteneurs adaptés */
    div[data-testid="stExpander"], .metric-card {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 12px;
        padding: 15px;
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .status-active { 
        background-color: rgba(34, 197, 94, 0.2); 
        color: #22c55e; 
        border: 1px solid rgba(34, 197, 94, 0.4);
    }
    
    /* Ajustement des boutons */
    .stButton>button {
        border-radius: 8px;
        border: 1px solid rgba(128, 128, 128, 0.3);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        border-color: #2563eb;
        color: #2563eb;
    }
</style>
""",
    unsafe_allow_html=True,
)

DATA_FILE = Path("atlas_data.json")
GEMINI_MODEL = "gemini-3.6-flash"

MATIERES_PAR_SEMESTRE = {
    "Tous les semestres": ["🌐 Chat Général / Tous les cours"],
    "Semestre 1 (S1)": [
        "🌐 cours S1",
        "Introduction aux sciences de gestion",
        "Histoire de la pensée et des techniques managériales",
        "Introduction au droit",
        "Théories économiques et enjeux contemporains",
        "Micro-économie",
        "Expression écrite et orale",
        "Fondamentaux de comptabilité",
        "Informatique d'usage",
        "LV1 Anglais",
        "Accompagnement à la réussite de mon projet 1",
    ],
    "Semestre 2 (S2)": [
        "🌐 cours S2",
        "Comptabilité générale",
        "Statistiques pour gestionnaires 1",
        "Droit commercial",
        "Marketing : histoire et réalités contemporaines",
        "Négociation commerciale",
        "Géopolitique",
        "Sociologie de la consommation",
        "Informatique d'usage",
        "LV1 Anglais",
    ],
    "Semestre 3 (S3)": [
        "🌐 cours S3",
        "Marketing stratégique",
        "Techniques quantitatives de gestion",
        "Mathématiques financières",
        "Droit social",
        "Droit des sociétés",
        "Le manager face aux défis du numérique et de l'environnement",
        "Théorie des organisations",
        "LV1 Anglais",
        "Accompagnement à la réussite de mon projet 2",
    ],
    "Semestre 4 (S4)": [
        "🌐 cours S4",
        "Comptabilité de gestion",
        "Marketing opérationnel",
        "Droit fiscal",
        "Statistiques pour gestionnaires 2",
        "Technologies du web",
        "Projet",
        "Entrepreneuriat",
        "Management de l'innovation",
        "LV1 Anglais",
        "Business game",
    ],
}

LISTE_MATIERES = [m for liste in MATIERES_PAR_SEMESTRE.values() for m in liste]

# ============================================================
# GESTION DES PREFÉRENCES ET DONNÉES LOCALES
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
    data.setdefault("cours_rediges", {})
    data.setdefault("notes_specifiques", {})
    data.setdefault(
        "long_term_memory",
        [
            "L'étudiant prépare une Licence Gestion.",
            "Préfère des explications concises avec des exemples pratiques.",
        ],
    )
    data.setdefault(
        "stats",
        {"quizzes_done": 0, "flashcards_generated": 0, "concepts_mastered": 0},
    )

    for matiere in LISTE_MATIERES:
        data["notes_specifiques"].setdefault(matiere, "")
        data["cours_rediges"].setdefault(matiere, "")

    return data

def save_data(data):
    try:
        with DATA_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Erreur de sauvegarde : {e}")

if "data" not in st.session_state:
    st.session_state.data = load_data()

# Historique des chats propre à la session utilisateur
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}

# ============================================================
# EXTRACTION CIBLÉE OBSIDIAN & PDF
# ============================================================

def parse_obsidian_vault_for_course(vault_path, selected_matiere):
    if not vault_path or not os.path.exists(vault_path):
        return ""

    content = ""
    clean_course_name = (
        selected_matiere.replace("S1 - ", "")
        .replace("S2 - ", "")
        .replace("S3 - ", "")
        .replace("S4 - ", "")
        .lower()
    )
    is_global = "🌐" in selected_matiere

    for root, dirs, files in os.walk(vault_path):
        for file in files:
            if file.startswith(".") or ".obsidian" in root:
                continue

            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, vault_path)

            if not is_global:
                file_rel_lower = rel_path.lower()
                keywords = [
                    k
                    for k in clean_course_name.split()
                    if len(k) > 3 and k not in ["tous", "cours"]
                ]
                if keywords and not any(kw in file_rel_lower for kw in keywords):
                    continue

            if file.lower().endswith(".md"):
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        file_text = f.read()
                        if file_text.strip():
                            content += (
                                f"\n--- DOCUMENT OBSIDIAN ({rel_path}) ---\n"
                                + file_text
                                + "\n"
                            )
                except Exception:
                    pass

            elif file.lower().endswith(".pdf"):
                try:
                    reader = PdfReader(file_path)
                    pdf_text = ""
                    for page in reader.pages:
                        pdf_text += page.extract_text() or ""
                    if pdf_text.strip():
                        content += (
                            f"\n--- PDF DU COURS ({rel_path}) ---\n"
                            + pdf_text
                            + "\n"
                        )
                except Exception:
                    pass

    return content

# ============================================================
# MOTEUR GEMINI
# ============================================================

def build_system_instruction(
    selected_matiere, direct_course_text, file_context, notes_gen, notes_mat, memory_list
):
    base_role = f"Tu es Atlas, un coach pédagogique expert dédié exclusivement au cours : **{selected_matiere}**."

    memory_block = (
        "\n\n🧠 MÉMOIRE GLOBALE DE L'ÉTUDIANT :\n"
        + "\n".join([f"- {item}" for item in memory_list])
    )

    if direct_course_text.strip():
        course_block = f"\n\n📖 CONTENU OFFICIEL DU COURS (ÉCRIT DANS ATLAS) :\n{direct_course_text}"
    elif file_context.strip():
        course_block = f"\n\n📚 DOCUMENTS DE COURS (OBSIDIAN/PDF) :\n{file_context}"
    else:
        course_block = "\n\nAucun support de cours n'a été rédigé ou trouvé pour ce cours."

    notes_block = (
        f"\n\n📝 CONSIGNES / REMARQUES SPÉCIFIQUES :\n{notes_mat}\n\nNOTES GÉNÉRALES :\n{notes_gen}"
    )

    return f"""{base_role}

Consignes strictes :
1. Réponds spécifiquement dans le cadre du cours **{selected_matiere}**.
2. Base tes réponses en priorité absolue sur le contenu du cours fourni ci-dessous.
3. Reste clair, structuré et synthétique.{memory_block}{notes_block}{course_block}"""

def query_gemini(
    api_key, selected_matiere, messages, prompt, direct_course_text, file_context, notes_gen, notes_mat
):
    client = genai.Client(api_key=api_key.strip())
    system_instruction = build_system_instruction(
        selected_matiere,
        direct_course_text,
        file_context,
        notes_gen,
        notes_mat,
        st.session_state.data.get("long_term_memory", []),
    )

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
        config={"system_instruction": system_instruction, "temperature": 0.3},
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
    st.caption("toujours plus loin")

    st.divider()

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

    semestre = st.selectbox("📚 Semestre", list(MATIERES_PAR_SEMESTRE.keys()))
    selected_matiere = st.selectbox("Matière", MATIERES_PAR_SEMESTRE[semestre])

    st.divider()

    with st.expander("📂 Dossier Obsidian (Optionnel)", expanded=False):
        obs_path = st.text_input(
            "Chemin du Vault :",
            value=st.session_state.data.get("obsidian_vault_path", ""),
            placeholder="/Users/nom/Documents/MonVault",
        )
        if st.button("Enregistrer le chemin", use_container_width=True):
            st.session_state.data["obsidian_vault_path"] = obs_path
            save_data(st.session_state.data)
            st.success("Chemin mis à jour !")

    st.divider()
    if st.button(f"🔄 Effacer cette discussion", use_container_width=True):
        st.session_state.chat_history[selected_matiere] = [
            {"role": "assistant", "content": f"Espace d'apprentissage Atlas prêt pour {selected_matiere} !"}
        ]
        st.rerun()

# Initialisation du chat par matière
if selected_matiere not in st.session_state.chat_history:
    st.session_state.chat_history[selected_matiere] = [
        {"role": "assistant", "content": f"Espace d'apprentissage Atlas prêt pour {selected_matiere} !"}
    ]

# ============================================================
# BARRE SUPÉRIEURE ET ONGLETS
# ============================================================

direct_course = st.session_state.data["cours_rediges"].get(selected_matiere, "")
obsidian_context = parse_obsidian_vault_for_course(
    st.session_state.data.get("obsidian_vault_path", ""), selected_matiere
)

col_title, col_status = st.columns([3, 1])
with col_title:
    st.title(f"📌 {selected_matiere}")

with col_status:
    st.write("")
    if direct_course.strip():
        st.markdown(
            '<div style="text-align: right;"><span class="status-badge status-active">● Cours rédigé actif</span></div>',
            unsafe_allow_html=True,
        )
    elif obsidian_context.strip():
        st.markdown(
            '<div style="text-align: right;"><span class="status-badge status-active">● Fichiers liés trouvés</span></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="text-align: right;"><span style="background-color: #fef3c7; color: #b45309; padding: 4px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">⚠️ Aucun cours chargé</span></div>',
            unsafe_allow_html=True,
        )

tab_chat, tab_editor, tab_tracking = st.tabs(
    ["💬 Chat du cours", "📖 Mon Cours", "📊 Suivi & Remarques"]
)

# ============================================================
# ONGLET 1 : CHAT
# ============================================================

with tab_chat:
    st.markdown(f"##### ⚡ Générateurs rapides pour **{selected_matiere}**")
    c1, c2, c3, c4 = st.columns(4)

    prompt_generator = None

    with c1:
        if st.button("❓ QCM", use_container_width=True):
            prompt_generator = f"Génère un QCM de 5 questions basé spécifiquement sur le cours {selected_matiere} avec la correction."
            st.session_state.data["stats"]["quizzes_done"] += 1
            save_data(st.session_state.data)

    with c2:
        if st.button("✏️ Cas pratique", use_container_width=True):
            prompt_generator = f"Donne-moi un exercice ou cas pratique adapté au cours {selected_matiere}."

    with c3:
        if st.button("💡 Fiche de synthèse", use_container_width=True):
            prompt_generator = "Rédige une fiche de synthèse visuelle et structurée pour ce cours."
            st.session_state.data["stats"]["concepts_mastered"] += 1
            save_data(st.session_state.data)

    with c4:
        if st.button("🟨 Cartes Anki", use_container_width=True):
            prompt_generator = f"Génère 8 flashcards sur {selected_matiere} au format Anki (Question;Réponse) dans un bloc de code."
            st.session_state.data["stats"]["flashcards_generated"] += 8
            save_data(st.session_state.data)

    st.markdown("---")

    chat_history = st.session_state.chat_history[selected_matiere]

    for message in chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input(f"Pose ta question sur {selected_matiere}...")
    final_prompt = prompt_generator if prompt_generator else user_input

    if final_prompt:
        if not active_key:
            st.error("⚠️ Veuillez configurer votre clé API Gemini (dans .env, Streamlit Secrets ou la barre latérale).")
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
                        direct_course_text=direct_course,
                        file_context=obsidian_context,
                        notes_gen=st.session_state.data["notes_generales"],
                        notes_mat=st.session_state.data["notes_specifiques"].get(selected_matiere, ""),
                    )
                    full_response = st.write_stream(response_stream)
                    chat_history.append({"role": "assistant", "content": full_response})
                except Exception as e:
                    st.error(f"❌ Erreur API : {e}")

# ============================================================
# ONGLET 2 : ÉDITEUR DE COURS
# ============================================================

with tab_editor:
    st.subheader(f"📖 Espace de rédaction : {selected_matiere}")
    st.caption("Colle ou rédige ton cours directement ici. Atlas l'analysera immédiatement dans l'onglet Chat.")

    current_course_content = st.text_area(
        label="Contenu textuel du cours :",
        value=st.session_state.data["cours_rediges"].get(selected_matiere, ""),
        height=450,
        placeholder="Colle ton cours, tes fiches ou tes chapitres ici...",
    )

    if st.button("💾 Enregistrer le cours", use_container_width=True):
        st.session_state.data["cours_rediges"][selected_matiere] = current_course_content
        save_data(st.session_state.data)
        st.success(f"Cours de {selected_matiere} mis à jour !")
        st.rerun()

# ============================================================
# ONGLET 3 : SUIVI ET REMARQUES
# ============================================================

with tab_tracking:
    st.subheader(f"📝 Remarques et mémoire pour {selected_matiere}")

    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown(f"##### 📌 Consignes spécifiques à {selected_matiere}")
        spec_notes = st.text_area(
            "Consignes du prof, chapitres importants pour l'examen :",
            value=st.session_state.data["notes_specifiques"].get(selected_matiere, ""),
            height=200,
        )
        if spec_notes != st.session_state.data["notes_specifiques"].get(selected_matiere, ""):
            st.session_state.data["notes_specifiques"][selected_matiere] = spec_notes
            save_data(st.session_state.data)
            st.success("Remarques enregistrées !")

    with col_right:
        st.markdown("##### 🧠 Souvenirs globaux")
        memory_items = st.session_state.data.get("long_term_memory", [])
        for item in memory_items:
            st.info(f"• {item}")
