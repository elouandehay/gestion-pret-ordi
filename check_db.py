import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

print("--- Colonnes de la table ordinateurs ---")
# Cette commande demande à SQLite la structure de la table
infos = cursor.execute("PRAGMA table_info(ordinateurs)").fetchall()
for colonne in infos:
    print(colonne)

conn.close()
