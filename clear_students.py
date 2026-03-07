import sqlite3

DB_FILE = "database.db"

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS etudiants")

cur.execute("""
CREATE TABLE etudiants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_apprenant INTEGER,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    email TEXT NOT NULL,
    email_insa TEXT,
    boursier BOOL NOT NULL,
    ine TEXT,
    regime_scolarite TEXT NOT NULL,
    annee INTEGER DEFAULT NULL,
    en_scolarite BOOL DEFAULT 1
)
""")

conn.commit()
conn.close()
