import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import json
import os
import database  # Module de gestion SQLite

st.set_page_config(page_title="Atlas Coach", page_icon="🎓", layout="wide")

FILES_DIR = "fichiers_cours"

# --- INITIALISATION DE LA BASE DE DONNÉES SQLITE ---
database.init_db()

# --- INSTRUCTIONS SYSTÈME POUR ATLAS ---
SYSTEM_INSTRUCTION = """
Tu es "Atlas", l'agent IA personnel et coach d'études de Faustine.
- Ton objectif principal : L'aider à réussir sa Licence 2 de Gestion (S3 & S4) ET lui faire rattraper son retard en anglais pour acquérir des bases très solides.
- Ton ton : Bienveillant, encourageant, très pédagogue, mais exigeant et structuré.

==================================================
🎯 OBJECTIF ANGLAIS : PROGRAMME DE REMISE À NIVEAU INTENSIF
==================================================
Faustine a de grosses lacunes en anglais et doit repartir sur des bases solides.
- Pédagogie adaptée : Explique toujours les concepts de grammaire et le vocabulaire de manière très simple, sans jargon inutile.
- Progressivité : Commence par les structures fondamentales (temps de base, construction de phrases, vocabulaire de la vie courante et du monde professionnel).
- Correction systématique : À chaque fois que Faustine essaie de répondre en anglais, corrige gentiment ses erreurs avec une petite explication claire.
- Mini-rituel : Propose-lui un "mot ou verbe du jour" en anglais avec sa traduction et une phrase d'exemple simple à la fin de tes messages.

==================================================
PROGRAMME ACADÉMIQUE DE FAUSTINE (L2 GESTION - PARCOURS GÉNÉRAL)
==================================================

📌 SEMESTRE 3 (L2 - Gestion) :
- UE 120-3-1 : Fondamentaux et outils de gestion
  - EC Marketing stratégique
  - EC Techniques quantitatives de gestion
  - EC Statistiques pour gestionnaires 2
- UE 120-3-2 : Environnement juridique
  - EC Droit social
  - EC Droit des sociétés
- UE 120-3-4 : Gestion - Management 2
  - EC Le manager face aux défis du numérique et de l'environnement
  - EC Théorie des organisations
- UE 120-3-0 : Unités transversales
  - EC LV1 Anglais (S3)
  - EC Accompagnement à la réussite de mon projet 2

❌ MATIÈRES EXCLUES (Parcours optionnels non choisis) :
- UE 120-3-5 : Gestion - Internationale 2

--------------------------------------------------

📌 SEMESTRE 4 (L2 - Gestion) :
- UE 120-4-1 : Piloter les organisations
  - EC Comptabilité de gestion
  - EC Marketing opérationnel
- UE 120-4-2 : Droit et finance
  - EC Droit fiscal
  - EC Mathématiques financières
- UE 120-4-3 : Traiter l'information
  - EC Technologies du web
  - EC Projet
- UE 120-4-4 : Gestion - Management 3
  - EC Entrepreneuriat
  - EC Management de l'innovation
- UE 120-4-0 : Unités transversales
  - EC LV1 Anglais (S4)
  - EC Business game

❌ MATIÈRES EXCLUES (Parcours optionnels non choisis) :
- UE 120-4-5 : Gestion - Internationale 3

==================================================
CONSIGNES & RÈGLES D'ACTION
==================================================
1. PÉDAGOGIE ACTIVE (Active Recall) :
   Ne donne jamais la réponse complète directement. Explique un concept de gestion ou une règle d'anglais simplement, puis pose-lui une question rapide pour vérifier qu'elle a compris.

2. ORGANISATION & SUIVI PRÉCIS :
   Aide Faustine à planifier ses semaines en alternant entre les révisions de ses cours de gestion et des petites sessions d'anglais (15-20 min/jour).

3. CONCENTRATION SUR LES ÉTUDES :
   Garde Faustine focalisée sur la réussite de sa L2 et sa progression en anglais.
"""

# --- GESTION DU STOCKAGE DES FICHIERS ---
def get_matiere_folder(selected_matiere):
    parts = selected_matiere.split(" - ", 1)
    semestre = parts[0]
    nom_matiere = parts[1] if len(parts) > 1 else selected_matiere
    folder_path = os.path.join(FILES_DIR, semestre, nom_matiere.replace("/", "_"))
    os.makedirs(folder_path, exist_ok=True)
    return folder_path

def save_uploaded_files(uploaded_files, target_folder):
    for uploaded_file in uploaded_files:
        file_path = os.path.join(target_folder, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

def read_all_matiere_files(folder_path):
    extracted_text = ""
    if not os.path.exists(folder_path):
        return extracted_text
        
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith('.pdf'):
            try:
                reader = PdfReader(file_path)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
            except Exception as e:
                st.warning(f"Impossible de lire le fichier {filename} : {e}")
        elif filename.endswith('.txt'):
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    extracted_text += f.read() + "\n"
            except Exception as e:
                st.warning(f"Impossible de lire le fichier {filename} : {e}")
    return extracted_text

MATIERES = {
    # SEMESTRE 1
    "S1 - Intro aux sciences de gestion": "Bienvenue en Intro aux sciences de gestion !",
    "S1 - Hist. pensée & techniques managériales": "Bienvenue en Histoire de la pensée managériale !",
    "S1 - Introduction au droit": "Bienvenue en Introduction au droit !",
    "S1 - Théories éco & enjeux contemporains": "Bienvenue en Théories économiques !",
    "S1 - Micro-économie": "Bienvenue en Micro-économie !",
    "S1 - Fondamentaux de comptabilité": "Bienvenue en Fondamentaux de comptabilité !",
    "S1 - Informatique d'usage": "Bienvenue en Informatique d'usage !",
    "S1 - LV1 Anglais": "Welcome to English class !",
    
    # SEMESTRE 2
    "S2 - Comptabilité générale": "Bienvenue en Comptabilité générale !",
    "S2 - Statistiques pour gestionnaires 1": "Bienvenue en Statistiques 1 !",
    "S2 - Droit commercial": "Bienvenue en Droit commercial !",
    "S2 - Marketing: histoire & réalités": "Bienvenue en Marketing !",
    "S2 - Négociation commerciale": "Bienvenue en Négociation commerciale !",
    "S2 - Géopolitique": "Bienvenue en Géopolitique !",
    "S2 - Sociologie de la consommation": "Bienvenue en Sociologie de la consommation !",
    "S2 - LV1 Anglais": "Welcome to English class !",

    # SEMESTRE 3
    "S3 - Marketing stratégique": "Bienvenue en Marketing stratégique !",
    "S3 - Techniques quantitatives de gestion": "Bienvenue en TQG !",
    "S3 - Statistiques pour gestionnaires 2": "Bienvenue en Statistiques 2 !",
    "S3 - Droit social": "Bienvenue en Droit social !",
    "S3 - Droit des sociétés": "Bienvenue en Droit des sociétés !",
    "S3 - Le manager face aux défis du numérique": "Bienvenue en Numérique & Environnement !",
    "S3 - Théorie des organisations": "Bienvenue en Théorie des organisations !",
    "S3 - LV1 Anglais": "Welcome to English class !",
   
    # SEMESTRE 4
    "S4 - Comptabilité de gestion": "Bienvenue en Comptabilité de gestion !",
    "S4 - Marketing opérationnel": "Bienvenue en Marketing opérationnel !",
    "S4 - Droit fiscal": "Bienvenue en Droit fiscal !",
    "S4 - Mathématiques financières": "Bienvenue en Mathématiques financières !",
    "S4 - Technologies du web": "Bienvenue en Technologies du web !",
    "S4 - Projet": "Bienvenue dans l'espace Projet !",
    "S4 - Entrepreneuriat": "Bienvenue en Entrepreneuriat !",
    "S4 - Management de l'innovation": "Bienvenue en Management de l'innovation !",
    "S4 - LV1 Anglais": "Welcome to English class !",
    "S4 - Business game": "Bienvenue dans le Business Game !"
}

# Initialisation des états temporaires
if "qcm_data" not in st.session_state:
    st.session_state.qcm_data = {}
if "exercice_actuel" not in st.session_state:
    st.session_state.exercice_actuel = {}

# --- SIDEBAR ---
with st.sidebar:
    st.title("🎓 Atlas Coach")
    selected_matiere = st.selectbox("Sélectionne ton cours :", list(MATIERES.keys()))
    
    st.markdown("---")
    st.header("📄 Fichiers du cours")
    
    matiere_folder = get_matiere_folder(selected_matiere)
    
    uploaded_files = st.file_uploader(
        "Dépose tes cours (PDF, TXT) :",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        key=selected_matiere
    )

    if uploaded_files:
        save_uploaded_files(uploaded_files, matiere_folder)
        st.success(f"{len(uploaded_files)} fichier(s) enregistré(s) !")

    existing_files = os.listdir(matiere_folder)
    if existing_files:
        st.caption("📁 Fichiers enregistrés pour ce cours :")
        for f in existing_files:
            st.text(f"• {f}")

# --- AFFICHAGE PRINCIPAL ---
st.title(f"🎓 {selected_matiere}")

# ONGLETS DE TRAVAIL PAR MATIÈRE
tab_chat, tab_exo, tab_qcm, tab_errors = st.tabs([
    "💬 Tuteur Chat", 
    "📝 Exercices", 
    "❓ QCM", 
    "🔍 Pointer les Erreurs"
])

def call_gemini(prompt):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("⚠️ La clé API `GEMINI_API_KEY` n'est pas configurée dans les secrets Streamlit.")
        return None
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-3.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Erreur API : {e}")
        return None

# --- CHARGEMENT DE L'HISTORIQUE DEPUIS LA BASE SQLITE ---
chat_history = database.charger_messages(selected_matiere)

# Message de bienvenue automatique si aucun message n'existe pour cette matière
if not chat_history:
    welcome_msg = MATIERES[selected_matiere]
    database.sauvegarder_message(selected_matiere, "assistant", welcome_msg)
    chat_history = database.charger_messages(selected_matiere)

# --- ONGLET 1 : CHAT TUTEUR ---
with tab_chat:
    for message in chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_input = st.chat_input("Pose ta question sur ce cours...")

    if user_input:
        database.sauvegarder_message(selected_matiere, "user", user_input)
        
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            texte_fichiers = read_all_matiere_files(matiere_folder)
            context_fichiers = f"\n\nDOCUMENTS DE COURS :\n{texte_fichiers[:15000]}" if texte_fichiers else ""
            
            prompt = (
                f"Aide l'étudiante pour le cours '{selected_matiere}'. "
                f"{context_fichiers}\n\nQuestion : {user_input}"
            )
            
            reply = call_gemini(prompt)
            if reply:
                st.write(reply)
                database.sauvegarder_message(selected_matiere, "assistant", reply)
                st.rerun()

# --- ONGLET 2 : EXERCICES PRATIQUES ---
with tab_exo:
    st.subheader(f"📝 Exercices d'application - {selected_matiere}")
    st.write("Génère un exercice sur mesure (cas pratique, problème de calcul, ou mise en pratique d'anglais) basé sur tes cours.")
    
    if st.button("🎲 Générer un nouvel exercice", key=f"btn_exo_{selected_matiere}"):
        texte_fichiers = read_all_matiere_files(matiere_folder)
        prompt_exo = (
            f"Crée un exercice pratique court et adapté au niveau L2 Gestion pour la matière '{selected_matiere}'. "
            f"L'exercice doit comporter une mise en situation et 1 ou 2 questions précises. Ne donne pas la réponse tout de suite. "
            f"Contenu des cours enregistrés : {texte_fichiers[:10000]}"
        )
        exercice_genere = call_gemini(prompt_exo)
        if exercice_genere:
            st.session_state.exercice_actuel[selected_matiere] = exercice_genere

    if selected_matiere in st.session_state.exercice_actuel:
        st.info(st.session_state.exercice_actuel[selected_matiere])
        
        reponse_etudiante = st.text_area("Ta réponse / tes calculs :", height=150, key=f"area_exo_{selected_matiere}")
        
        if st.button("📤 Soumettre ma réponse pour correction", key=f"sub_exo_{selected_matiere}"):
            if reponse_etudiante:
                prompt_correction = (
                    f"Voici l'exercice proposé pour le cours '{selected_matiere}' :\n"
                    f"{st.session_state.exercice_actuel[selected_matiere]}\n\n"
                    f"Voici la réponse proposée par Faustine :\n{reponse_etudiante}\n\n"
                    f"Évalue sa réponse. Donne une correction détaillée, bienveillante mais rigoureuse, en soulignant les points forts et les erreurs commises."
                )
                correction = call_gemini(prompt_correction)
                if correction:
                    st.markdown("### 📋 Correction d'Atlas :")
                    st.write(correction)
            else:
                st.warning("Écris ta réponse avant de valider.")

# --- ONGLET 3 : QCM INTERACTIF ---
with tab_qcm:
    st.subheader(f"🧪 QCM de révision - {selected_matiere}")
    
    if st.button("🔄 Générer un QCM (3 questions)", key=f"btn_qcm_{selected_matiere}"):
        texte_fichiers = read_all_matiere_files(matiere_folder)
        prompt_qcm = (
            f"Génère un QCM de 3 questions à choix multiples sur le cours '{selected_matiere}'. "
            f"Consigne stricte : Réponds UNIQUEMENT sous la forme d'un tableau JSON valide, sans balises markdown, sans texte additionnel. "
            f"Structure requise :\n"
            f'[\n  {{\n    "question": "Texte question",\n    "options": ["A", "B", "C", "D"],\n    "reponse": "Option exacte",\n    "explication": "Pourquoi c\'est juste"\n  }}\n]\n'
            f"Contenu des cours : {texte_fichiers[:10000]}"
        )
        res = call_gemini(prompt_qcm)
        if res:
            try:
                clean_res = res.replace("```json", "").replace("```", "").strip()
                st.session_state.qcm_data[selected_matiere] = json.loads(clean_res)
            except Exception:
                st.warning("Erreur lors de la génération du QCM. Clique à nouveau sur le bouton.")

    if selected_matiere in st.session_state.qcm_data and st.session_state.qcm_data[selected_matiere]:
        with st.form(f"qcm_form_{selected_matiere}"):
            user_answers = {}
            for idx, q in enumerate(st.session_state.qcm_data[selected_matiere]):
                st.markdown(f"**Q{idx+1}. {q['question']}**")
                user_answers[idx] = st.radio("Choisis ta réponse :", q["options"], key=f"qcm_{selected_matiere}_{idx}")
                st.markdown("---")
            
            submitted = st.form_submit_button("Valider mes réponses")
            if submitted:
                score = 0
                for idx, q in enumerate(st.session_state.qcm_data[selected_matiere]):
                    ans = user_answers[idx]
                    if ans == q["reponse"]:
                        st.success(f"Q{idx+1} : Correct ! 🎉")
                        score += 1
                    else:
                        st.error(f"Q{idx+1} : Incorrect. Tu as répondu : {ans}. La bonne réponse est : **{q['reponse']}**")
                    st.info(f"💡 Explication : {q['explication']}")
                st.metric("Score final", f"{score} / {len(st.session_state.qcm_data[selected_matiere])}")

# --- ONGLET 4 : POINTER LES ERREURS ---
with tab_errors:
    st.subheader(f"🔍 Analyse d'erreurs - {selected_matiere}")
    st.write("Colle ici une réponse d'examen, un exercice rédigé ou un paragraphe en anglais pour qu'Atlas détecte et explique tes fautes.")
    
    student_submission = st.text_area("Ton texte à vérifier :", height=150, key=f"err_input_{selected_matiere}")
    
    if st.button("🔎 Analyser mes erreurs", key=f"btn_err_{selected_matiere}"):
        if student_submission:
            texte_fichiers = read_all_matiere_files(matiere_folder)
            prompt_err = (
                f"Analyse le texte suivant écrit par l'étudiante Faustine dans le cadre du cours '{selected_matiere}'.\n\n"
                f"Texte à analyser : {student_submission}\n\n"
                f"Consignes :\n"
                f"1. Identifie précisément les fautes (concepts erronés, erreurs de calcul en gestion ou fautes de grammaire/vocabulaire en anglais).\n"
                f"2. Explique simplement pourquoi c'est incorrect.\n"
                f"3. Donne la correction optimale ainsi qu'un conseil de révision.\n"
                f"Documents du cours : {texte_fichiers[:10000]}"
            )
            analysis = call_gemini(prompt_err)
            if analysis:
                st.markdown("### 📋 Rapport d'analyse d'Atlas :")
                st.write(analysis)
        else:
            st.warning("Merci d'écrire ou de me coller un texte à examiner.")
