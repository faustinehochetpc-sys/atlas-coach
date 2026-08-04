import streamlit as st
import google.generativeai as genai

st.title("🎓 Atlas - Test des modèles")

try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    st.write("### Modèles disponibles pour ta clé API :")
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
            
    st.write(available_models)

except Exception as e:
    st.error(f"Erreur lors de la récupération des modèles : {e}")
