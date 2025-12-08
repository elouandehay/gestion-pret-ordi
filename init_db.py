import sqlite3
import bcrypt  

connection = sqlite3.connect('database.db')

with open('schema.sql') as f:
    connection.executescript(f.read())

password = "password123".encode('utf-8')
hashed = bcrypt.hashpw(password, bcrypt.gensalt())


try:
    connection.execute("INSERT INTO administrateurs (username, password_hash) VALUES (?, ?)", ('admin', hashed))
    print("Admin créé : identifiant = 'admin', mot de passe = 'password123'")
    
except sqlite3.OperationalError:
    print("Erreur : La table 'administrateurs' n'existe pas dans schema.sql")


connection.commit()
connection.close()
print("Base de données initialisée avec succès !")
