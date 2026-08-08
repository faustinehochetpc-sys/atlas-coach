import os
import streamlit as st
import google.generativeai as genai

def search_in_course_files(matiere_folder, query):
    """
    Recherche dans les fichiers textes/extraits du dossier de la matière
    et renvoie les passages les plus pertinents pour la question posée.
    """
    if not os.path.exists(matiere_folder):
        return ""

    all_text = ""
    for filename in os.listdir(matiere_folder):
        file_path = os.path.join(filename)
        # Compléter le chemin complet
        full_path = os.path.join(matiere_folder, filename)
        
        if filename.endswith('.txt') or filename.endswith('.pdf'):
            # Lecture du fichier s'il existe
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    all_text += f.read() + "\n"
            except Exception:
                pass

    if not all_text:
        return ""

    # Découpage du texte en blocs (chunks)
    chunks = [all_text[i:i+2000] for i in range(0, len(all_text), 1500)]
    
    # Filtrage simple des blocs contenant des mots-clés de la question
    query_words = set(query.lower().split())
    relevant_chunks = []
    
    for chunk in chunks:
        chunk_lower = chunk.lower()
        if any(word in chunk_lower for word in query_words if len(word) > 3):
            relevant_chunks.append(chunk)

    # Si aucun bloc spécifique n'est trouvé, on prend les premiers blocs par défaut
    if not relevant_chunks:
        relevant_chunks = chunks[:5]

    return "\n---\n".join(relevant_chunks[:5])
