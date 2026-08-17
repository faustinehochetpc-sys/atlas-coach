import streamlit as st
import requests
import json
import os

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Atlas Dashboard - Learning & Revision",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Fonction pour connecter et envoyer des cartes à Anki (via AnkiConnect)
def add_card_to_anki(front, back, deck_name="Licence Gestion::Atlas"):
    anki_url = "http://127.0.0.1:8765"
    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": deck_name,
                "modelName": "Basic",
                "fields": {
                    "Front": front,
                    "Back": back
                },
                "options": {
                    "allowDuplicate": False
                },
                "tags": ["atlas", "streamlit_auto"]
            }
        }
    }
    try:
        response = requests.post(anki_url, json=payload, timeout=3)
        result = response.json()
        if result.get("error") is None:
            return True, "Flashcard envoyée avec succès à Anki !"
        else:
            return False, f"Erreur Anki : {result.get('error')}"
    except Exception as e:
        return False, "Impossible de joindre Anki. Vérifiez qu'Anki est ouvert sur votre ordinateur."

# Navigation
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/graduation-cap.png", width=70)
    st.title("Atlas Cockpit")
    st.caption("Système d'Apprentissage Actif & Suivi")
    st.divider()
    
    menu = st.radio(
        "Navigation",
        ["📊 Tableau de bord", "📝 Centre de QCM", "🃏 Envoi Flashcards Anki", "📚 Bibliothèque de cours"],
        index=0
    )
    
    st.divider()
    st.markdown("### 🔌 Statut des Moteurs")
    st.success("🟢 Obsidian Vault (Connecté)")
    
    # Vérification automatique de l'état d'AnkiConnect
    try:
        res = requests.post("http://127.0.0.1:8765", json={"action": "version", "version": 6}, timeout=1)
        if res.status_code == 200:
            st.success("🟢 AnkiConnect (Actif)")
        else:
            st.warning("🟠 AnkiConnect (Inaccessible)")
    except:
        st.error("🔴 Anki (Fermé / Déconnecté)")

# En-tête principal
st.markdown('<div class="main-header">🎓 Projet ATLAS — Plateforme de Révision</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. TABLEAU DE BORD
# ---------------------------------------------------------
if menu == "📊 Tableau de bord":
    st.markdown('<div class="sub-header">Vue d\'ensemble de ta progression par semestre et par matière.</div>', unsafe_allow_html=True)
    
    # Indicateurs de performance
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Moyenne QCM", value="80%", delta="+5%")
    with col2:
        st.metric(label="Cartes Anki Ancrées", value="142", delta="+12 cette semaine")
    with col3:
        st.metric(label="Heures de Révision", value="18.5h", delta="+2.5h")
    with col4:
        st.metric(label="Objectif Semestre S4", value="65%", delta="En bonne voie")
        
    st.divider()
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📈 Avancement par Matière (Semestre S4)")
        matieres = {
            "Comptabilité de gestion": 0.85,
            "Droit fiscal": 0.60,
            "Marketing opérationnel": 0.90,
            "Technologie du Web": 0.75,
            "Mathématiques financières": 0.40,
            "Anglais 3": 0.95
        }
        for mat, progress in matieres.items():
            st.write(f"**{mat}** ({int(progress*100)}%)")
            st.progress(progress)
            
    with col_right:
        st.subheader("📋 Dernières Activités")
        st.info("**Comptabilité de gestion**\n\nQCM • Score: 4/5 (Aujourd'hui)")
        st.info("**Droit fiscal**\n\nFlashcards • 10 cartes ajoutées (Hier)")

# ---------------------------------------------------------
# 2. CENTRE DE QCM & EXERCICES
# ---------------------------------------------------------
elif menu == "📝 Centre de QCM":
    st.markdown('<div class="sub-header">Entraîne-toi sur les exercices générés par l\'IA depuis tes cours.</div>', unsafe_allow_html=True)
    
    matiere_choisie = st.selectbox("Sélectionne la matière à réviser :", ["Comptabilité de gestion", "Droit fiscal", "Technologie du Web"])
    
    st.divider()
    
    st.subheader("Question 1 : Seuil de Rentabilité")
    st.write("*Dans le calcul du seuil de rentabilité en valeur, quelle est la formule exacte ?*")
    
    option = st.radio(
        "Choisis la réponse correcte :",
        [
            "A) Charges Fixes / Taux de Marge sur Coût Variable",
            "B) Charges Variables / Chiffre d'Affaires",
            "C) Chiffre d'Affaires - Charges Fixes",
            "D) Marge sur Coût Variable x Charges Fixes"
        ]
    )
    
    if st.button("Valider ma réponse", type="primary"):
        if option.startswith("A"):
            st.success("🎉 Bravo ! Excellente réponse. Le seuil de rentabilité (SR) est bien égal aux Charges Fixes divisées par le Taux de MCV.")
            st.balloons()
        else:
            st.error("❌ Faux. Réponse correcte : **A) Charges Fixes / Taux de Marge sur Coût Variable**.")
            st.info("💡 **Rappel du cours** : SR (en valeur) = CF / tMCV, où tMCV = MCV / CA.")

# ---------------------------------------------------------
# 3. ENVOI FLASHCARDS ANKI
# ---------------------------------------------------------
elif menu == "🃏 Envoi Flashcards Anki":
    st.markdown('<div class="sub-header">Crée une carte Anki rapide et envoie-la directement dans ton logiciel.</div>', unsafe_allow_html=True)
    
    with st.form("anki_form"):
        deck = st.text_input("Nom du paquet Anki", value="Licence Gestion::S4::Comptabilité")
        front_text = st.text_area("Recto (Question / Définition) :", placeholder="Ex: Définition de la Marge sur Coût Variable (MCV)")
        back_text = st.text_area("Verso (Réponse / Formule) :", placeholder="Ex: Chiffre d'Affaires minus Charges Variables (CA - CV)")
        
        submitted = st.form_submit_button("🚀 Envoyer directement dans Anki")
        
        if submitted:
            if front_text and back_text:
                success, msg = add_card_to_anki(front_text, back_text, deck)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
            else:
                st.warning("Veuillez remplir le recto et le verso de la carte.")

# ---------------------------------------------------------
# 4. BIBLIOTHÈQUE DE COURS
# ---------------------------------------------------------
elif menu == "📚 Bibliothèque de cours":
    st.markdown('<div class="sub-header">Consulte les synthèses générées depuis ton coffre Obsidian.</div>', unsafe_allow_html=True)
    
    cours_dispo = st.selectbox("Choisir un chapitre :", ["Comptabilité_Chapitre_1_Bilan.md", "Droit_Fiscal_TVA.md"])
    
    if cours_dispo == "Comptabilité_Chapitre_1_Bilan.md":
        st.markdown("""
        ### 📌 Synthèse : Le Bilan Comptable (ATLAS Format)
        
        #### 1. Concept Clé
        Le bilan est un tableau représentant la situation patrimoniale de l'entreprise à un instant T.
        * **Actif** (Emplois) : Ce que l'entreprise possède (Immobilisations, Stocks, Créances, Trésorerie).
        * **Passif** (Ressources) : Ce que l'entreprise doit (Capitaux propres, Dettes financières, Dettes fournisseurs).
        
        #### 2. Équilibre Fondamental
        $$\\text{Actif Total} = \\text{Passif Total}$$
        
        #### 3. Formules Importantes
        * **Fonds de Roulement Net Global (FRNG)** = Capitaux Permanents - Actifs Immobilisés
        * **Besoin en Fonds de Roulement (BFR)** = Actif Circulant - Passif Circulant
        """)
