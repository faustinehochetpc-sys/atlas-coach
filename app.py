import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import json
import os

st.set_page_config(page_title="Atlas - Coach & Dashboard", page_icon="🎓", layout="wide")

DATA_FILE = "atlas_data.json"

# --- LISTE DES MATIÈRES DU PARCOURS MANAGEMENT ---
LISTE_MATIERES = [
    "🌐 Chat Général / Tous les cours",
    # Semestre 1
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
    # Semestre 2
    "S2 - Comptabilité générale",
    "S2 - Statistiques pour gestionnaires 1",
    "S2 - Droit commercial",
    "S2 - Marketing : histoire et réalités contemporaines",
    "S2 - Négociation commerciale",
    "S2 - Géopolitique",
    "S2 - Sociologie de la consommation",
    "S2 - Informatique d'usage",
    "S2 - LV1 Anglais",
    # Semestre 3
    "S3 - Marketing stratégique",
    "S3 - Techniques quantitatives de gestion",
    "S3 - Statistiques pour gestionnaires 2",
    "S3 - Droit social",
    "S3 - Droit des sociétés",
    "S3 - Le manager face aux défis du numérique et de l'environnement",
    "S3 - Théorie des organisations",
    "S3 - LV1 Anglais",
    "S3 - Accompagnement à la réussite de mon projet 2",
    # Semestre 4
    "S4 - Comptabilité de gestion",
    "S4 - Marketing opérationnel",
    "S4 - Droit fiscal",
    "S4 - Mathématiques financières",
    "S4 - Technologies du web",
    "S4 - Projet",
    "S4 - Entrepreneuriat",
    "S4 - Management de l'innovation",
    "S4 - LV1 Anglais",
    "S4 - Business game"
]

# --- CHARGEMENT ET SAUVEGARDE DES DONNÉES ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
            
    default_matieres = {}
    default_progression = {}
    
    for mat in LISTE_MATIERES:
        default_matieres[mat] = [
            {"role": "assistant", "content": f"Espace de travail prêt pour {mat} ! Pose tes questions ici."}
        ]
        default_progression[mat] = 0

    return {
        "profile": {
            "objectif": "Réussir mes examens et booster ma productivité",
            "style": "Explications simples avec exemples concrets",
            "obsidian_vault_path": ""
        },
        "matieres": default_matieres,
        "progression": default_progression
    }

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Erreur de sauvegarde : {e}")

# Initialisation de la session
if "data" not in st.session_state:
    st.session_state.data = load_data()

# Sécurité pour l'initialisation des matières
for mat in LISTE_MATIERES:
    if mat not in st.session_state.data["matieres"]:
        st.session_state.data["matieres"][mat] = [
            {"role": "assistant", "content": f"Espace de travail prêt pour {mat} !"}
        ]
    if "progression" not in st.session_state.data:
        st.session_state.data["progression"] = {}
    if mat not in st.session_state.data["progression"]:
        st.session_state.data["progression"][mat] = 0

# Extraction de texte pour PDF et TXT

    def extract_text_from_files_and_obsidian(uploaded_files):
        extracted_text = ""
    
    # 1. Lecture des PDF/TXT téléversés
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.name.endswith('.pdf'):
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
            elif uploaded_file.name.endswith('.txt'):
                extracted_text += uploaded_file.read().decode('utf-8') + "\n"
                
    # 2. Lecture automatique du dossier Obsidian
    vault_path = st.session_state.data["profile"].get("obsidian_vault_path", "")
    if vault_path and os.path.exists(vault_path):
        for root, _, files in os.walk(vault_path):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as md_file:
                            extracted_text += f"\n--- Note Obsidian ({file}) ---\n" + md_file.read()
                    except Exception:
                        pass
                        
    return extracted_text

# Formatage des messages pour export Anki
def generate_anki_export(messages):
    anki_content = "# Separator:;\n# html:true\n"
    for i in range(0, len(messages)-1, 2):
        if messages[i]["role"] == "user" and messages[i+1]["role"] == "assistant":
            question = messages[i]["content"].replace("\n", "<br>").replace(";", ",")
            answer = messages[i+1]["content"].replace("\n", "<br>").replace(";", ",")
            anki_content += f"{question};{answer}\n"
    return anki_content

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("🎓 Atlas")
    st.header("📚 Tes Cours & Matières")
    
    selected_matiere = st.selectbox("Sélectionne ton cours :", LISTE_MATIERES)
    
    st.markdown("---")
    st.header("📊 Progression du cours")
    current_prog = st.session_state.data["progression"].get(selected_matiere, 0)
    new_prog = st.slider("Avancement (%) :", 0, 100, int(current_prog), key=f"slider_{selected_matiere}")
    if new_prog != current_prog:
        st.session_state.data["progression"][selected_matiere] = new_prog
        save_data(st.session_state.data)
        st.rerun()

    st.markdown("---")
    if st.button("🔄 Réinitialiser ce cours"):
        st.session_state.data["matieres"][selected_matiere] = [
            {"role": "assistant", "content": f"Discussion réinitialisée pour {selected_matiere}."}
        ]
        st.session_state.data["progression"][selected_matiere] = 0
        save_data(st.session_state.data)
        st.rerun()

    st.markdown("---")
    st.header("📄 Fichiers du cours")
    uploaded_files = st.file_uploader(
        "Dépose tes cours (PDF, TXT) :",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        key=selected_matiere
    )

    st.markdown("---")
    # SECTION OBSIDIAN ET ANKI
    with st.expander("🔗 Obsidian & Anki Integrations"):
        obs_path = st.text_input(
            "Chemin du Coffre-fort Obsidian :", 
            value=st.session_state.data["profile"].get("obsidian_vault_path", "")
        )
        if st.button("💾 Enregistrer chemin Obsidian"):
            st.session_state.data["profile"]["obsidian_vault_path"] = obs_path
            save_data(st.session_state.data)
            st.success("Chemin Obsidian enregistré !")

        st.markdown("---")
        st.subheader("🎴 Exporter vers Anki")
        anki_data = generate_anki_export(st.session_state.data["matieres"][selected_matiere])
        st.download_button(
            label="📥 Télécharger fiches Anki (.txt)",
            data=anki_data,
            file_name=f"anki_{selected_matiere.replace(' ', '_')}.txt",
            mime="text/plain"
        )

    st.markdown("---")
    with st.expander("⚙️ Profil & Préférences"):
        prof_obj = st.text_input("Objectif :", value=st.session_state.data["profile"].get("objectif", ""))
        styles = ["Explications simples avec exemples concrets", "Synthétique et direct", "Détaillé et académique"]
        current_style = st.session_state.data["profile"].get("style", styles[0])
        style_idx = styles.index(current_style) if current_style in styles else 0
        
        prof_style = st.selectbox("Style de réponse :", styles, index=style_idx)
        
        if st.button("💾 Sauvegarder profil"):
            st.session_state.data["profile"]["objectif"] = prof_obj
            st.session_state.data["profile"]["style"] = prof_style
            save_data(st.session_state.data)
            st.success("Profil enregistré !")

# --- CONTENU PRINCIPAL ---
st.title(f"{selected_matiere}")
st.caption(f"Objectif : {st.session_state.data['profile']['objectif']} • Style : {st.session_state.data['profile']['style']}")

# Barre d'avancement globale du cours sélectionné
prog_val = st.session_state.data["progression"].get(selected_matiere, 0)
st.progress(prog_val / 100)
st.caption(f"Progression globale du module : {prog_val}%")

st.markdown("---")

# Affichage des messages
current_messages = st.session_state.data["matieres"][selected_matiere]
for message in current_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrée utilisateur
prompt = st.chat_input(f"Pose ta question pour {selected_matiere}...")

if prompt:
    current_messages.append({"role": "user", "content": prompt})
    save_data(st.session_state.data)
    
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        api_key = st.secrets.get("GEMINI_API_KEY")
        if not api_key:
            error_msg = "⚠️ La clé API `GEMINI_API_KEY` n'est pas configurée dans secrets.toml."
            st.warning(error_msg)
            current_messages.append({"role": "assistant", "content": error_msg})
            save_data(st.session_state.data)
        else:
            try:
                genai.configure(api_key=api_key)
                
                prof = st.session_state.data["profile"]
                if selected_matiere == "🌐 Chat Général / Tous les cours":
                    system_instruction = (
                        f"Tu es Atlas, un coach pédagogique personnel en Licence de Gestion.\n"
                        f"Objectif de l'élève : {prof.get('objectif')}\n"
                        f"Style d'explication : {prof.get('style')}\n"
                        "Aide l'élève de manière globale et transversale sur ses études et son organisation."
                    )
                else:
                    system_instruction = (
                        f"Tu es Atlas, un coach pédagogique expert pour la matière '{selected_matiere}' en Licence de Gestion.\n"
                        f"Objectif de l'élève : {prof.get('objectif')}\n"
                        f"Style d'explication : {prof.get('style')}\n"
                        "Adapte tes réponses à ce cours et réponds de manière claire et structurée."
                    )
                
                context_text = ""
                all_text = extract_text_from_files_and_obsidian(uploaded_files)
                if all_text:
                    context_text = f"\n\nCONTENU DES COURS ET NOTES OBSIDIAN :\n{all_text[:6000]}"
                
                full_prompt = f"{system_instruction}{context_text}\n\nQuestion : {prompt}"
                
                model = genai.GenerativeModel("gemini-3.5-flash")
                response = model.generate_content(full_prompt)
                
                st.markdown(response.text)
                current_messages.append({"role": "assistant", "content": response.text})
                save_data(st.session_state.data)
                
            except Exception as e:
                st.error(f"Erreur : {e}")
