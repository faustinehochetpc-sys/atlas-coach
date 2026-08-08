import sqlite3

# Nom du fichier de base de données SQLite
DB_NAME = "atlas.db"

def init_db():
    """
    Initialise la base de données et crée la table 'messages' si elle n'existe pas.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Création de la table des messages de chat
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            matiere TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def sauvegarder_message(matiere: str, role: str, content: str):
    """
    Sauvegarde un message (utilisateur ou assistant) dans la base de données.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO messages (matiere, role, content)
        VALUES (?, ?, ?)
    ''', (matiere, role, content))
    
    conn.commit()
    conn.close()

def charger_messages(matiere: str):
    """
    Récupère tous les messages d'une matière donnée sous forme de liste de dictionnaires.
    Exemple de retour : [{"role": "user", "content": "Bonjour"}, ...]
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT role, content FROM messages
        WHERE matiere = ?
        ORDER BY id ASC
    ''', (matiere,))
    
    rows = cursor.fetchall()
    conn.close()
    
    # On transforme le résultat de la base de données au format attendu par Streamlit
    messages = [{"role": row[0], "content": row[1]} for row in rows]
    return messages
