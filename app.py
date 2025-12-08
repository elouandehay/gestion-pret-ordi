from flask import Flask, render_template, request, redirect, url_for, session, flash
#from models import *
#from config import *
from datetime import datetime
import sqlite3
from functools import wraps
import bcrypt


app = Flask(__name__)
app.secret_key ='3757983889c72c54cb6c98760ca81d3ba40e9ac275062a86266d2816711c24d4'

# Fonction pour se connecter à la base SQLite
def get_db_connection():
    conn=sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

#sert à protéger les pages
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
    
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_input = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM administrateurs WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user:
            stored_hash = user['password_hash']
            
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')
            

            try:
                if bcrypt.checkpw(password_input.encode('utf-8'), stored_hash):
                    session['user'] = user['username']
                    return redirect(url_for('index'))
                else:
                    flash("Mot de passe incorrect")
            except ValueError:
                flash("Erreur de format du mot de passe")
        else:
            flash("Utilisateur inconnu")
            
    return render_template('login.html')
    
@app.route('/logout')
def logout():
    session.pop('user', None) # On vide la session
    return redirect(url_for('login'))

# Page principale : afficher tous les ordinateurs
@app.route("/")
@login_required #permet d'obliger le login
def index():
    conn = get_db_connection()
    ordinateurs = conn.execute('SELECT * FROM ordinateurs').fetchall()
    conn.close()
    return render_template('index.html',ordinateurs=ordinateurs)


#emprunter un ordinateur
@app.route('/emprunter/<int:id>', methods=('POST',))
@login_required
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
@login_required
def rendre(id):
    conn = get_db_connection()
    conn.execute('UPDATE ordinateurs SET etat = ?, emprunteur = ? WHERE id = ?',
                 ('disponible', None, id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/ajouter', methods=['GET', 'POST'])
@login_required
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
