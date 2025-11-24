from flask import Flask, render_template, request, redirect
#from models import *
#from config import *
from datetime import datetime
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn=sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
    
@app.route("/")
def index():
    conn = get_db_connection()
    ordinateurs = conn.execute('SELECT * FROM ordinateurs').fetchall()
    conn.close()
    return render_template('index.html',ordinateurs=ordinateurs)

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

if __name__ == '__main__':
    app.run(debug=True)
