from flask import Flask, render_template, request, redirect, url_for
#from models import *
#from config import *
from datetime import datetime
import sqlite3

app = Flask(__name__)
# Fonction pour se connecter à la base SQLite
def get_db_connection():
    conn=sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Page principale : afficher tous les ordinateurs
@app.route("/")
def index():
    conn = get_db_connection()
    ordinateurs = conn.execute('SELECT * FROM ordinateurs').fetchall()
    conn.close()
    return render_template('index.html',ordinateurs=ordinateurs)


#emprunter un ordinateur
@app.route('/emprunter/<int:id>', methods=('POST',))
def emprunter(id):
    eleve = request.form['eleve']
    
    if eleve:
        conn = get_db_connection()
        conn.execute('UPDATE ordinateurs SET etat = ?, emprunteur = ? WHERE id = ?',
                     ('emprunte', eleve, id))
        conn.commit()
        conn.close()
        
    return redirect(url_for('index'))

#Action : Rendre un PC
@app.route('/rendre/<int:id>', methods=('POST',))
def rendre(id):
    conn = get_db_connection()
    conn.execute('UPDATE ordinateurs SET etat = ?, emprunteur = ? WHERE id = ?',
                 ('disponible', None, id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
    if request.method == 'POST':
        nom_pc = request.form.get('nom_pc') #recupère la valeur du nom rempli dans le formulaire
        if nom_pc:#vérifie que le nom n'est pas vide
            conn = get_db_connection()#se connecte a la base de donné
            conn.execute('INSERT INTO ordinateurs (nom, etat) VALUES (?, ?)',
                         (nom_pc, 'disponible'))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    # Si méthode GET, afficher le formulaire
    return render_template('ajouter.html')

if __name__ == '__main__':
    app.run(debug=True)
