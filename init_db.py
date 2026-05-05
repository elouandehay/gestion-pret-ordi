import sqlite3
import bcrypt  
import os

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

raw_password = os.environ.get('ADMIN_PASSWORD', 'default_dev_password')
password = raw_password.encode('utf-8')

hashed = bcrypt.hashpw(password, bcrypt.gensalt())

try:
    connection.execute("INSERT INTO administrateurs (username, password_hash) VALUES (?, ?)", ('admin', hashed))
    print(f"Admin créé avec succès.")
    
except sqlite3.OperationalError:
    print("Erreur : La table 'administrateurs' n'existe pas dans schema.sql")
except sqlite3.IntegrityError:
    print("L'admin existe déjà.")

connection.commit()
connection.close()
print("Base de données initialisée avec succès !")
