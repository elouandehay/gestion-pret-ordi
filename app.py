from flask import Flask, render_template, request, redirect, url_for, session, flash
#from models import *
#from config import *
from datetime import datetime
import sqlite3
from functools import wraps
import bcrypt

import os
from flask import request, redirect, url_for, render_template, send_file
from werkzeug.utils import secure_filename

from Convention.generation_convention import generer_convention 
from update_etudiants import process_etudiants

app = Flask(__name__)
app.secret_key ='3757983889c72c54cb6c98760ca81d3ba40e9ac275062a86266d2816711c24d4'

#AJOUT SÉCURITÉ HTTPS
#Empêche le cookie d'être envoyé si on n'est pas en HTTPS
app.config['SESSION_COOKIE_SECURE'] = True

#Empêche JavaScript de lire le cookie (contre les failles XSS)
app.config['SESSION_COOKIE_HTTPONLY'] = True
#Protège contre les sites externes qui voudraient utiliser les cookies
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

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
    
@app.route('/historique/<path:numero_serie>')
@login_required
def historique(numero_serie):
    conn = get_db_connection()

    historique = conn.execute("""
        SELECT nom, prenom, email, date_pret, date_retour
        FROM historique_prets
        WHERE ordinateur_id = ?
        ORDER BY date_retour DESC
    """, (numero_serie,)).fetchall()

    conn.close()

    return render_template(
        'historique.html',
        historique=historique,
        numero_serie=numero_serie
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_input = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM administrateurs WHERE username = ?', (username,)).fetchone()
        conn.close()

        # On définit un hash bidon pour simuler le calcul si l'user n'existe pas
        fake_hash = b'$2b$12$L9K.O5Z1v6sV7VvE8t7T7.z0P0Y0X0W0V0U0T0S0R0Q0P0O0N0M0L'

        if user:
            target_hash = user['password_hash']
            if isinstance(target_hash, str):
                target_hash = target_hash.encode('utf-8')
            
            # Vérification réelle
            valid = bcrypt.checkpw(password_input.encode('utf-8'), target_hash)
        else:
            # On simule le travail de bcrypt pour perdre du temps
            bcrypt.checkpw(password_input.encode('utf-8'), fake_hash)
            valid = False

        if valid:
            session['user'] = user['username']
            return redirect(url_for('index'))
        else:
            flash("Identifiant ou mot de passe incorrect") # Message générique !
            
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
    ordinateurs = conn.execute("""
        SELECT o.numero_serie, o.numero_inventaire, o.modele, o.date_sortie, o.dispo,
               e.nom, e.prenom,
               p.caution_prof_validee, p.caution_compta_validee
        FROM ordinateurs o
        LEFT JOIN prets p ON o.numero_serie = p.ordinateur_id AND o.dispo = 0
        LEFT JOIN etudiants e ON p.etudiant_id = e.id
        ORDER BY o.date_sortie ASC
    """).fetchall()
    commentaires = conn.execute("""
            SELECT ordinateur_id, commentaire, date_commentaire
            FROM commentaires
            ORDER BY date_commentaire DESC
        """).fetchall()
    conn.close()

    commentaires_dict = {}
    for c in commentaires:
        if c['ordinateur_id'] not in commentaires_dict:
            commentaires_dict[c['ordinateur_id']] = []
        commentaires_dict[c['ordinateur_id']].append(c)
    return render_template('index.html',ordinateurs=ordinateurs, commentaires_dict=commentaires_dict)


# Emprunter un ordinateur (acceptant aussi les élèves non présents dans la base)
@app.route('/emprunter/<path:numero_serie>', methods=('POST',))
@login_required
def emprunter(numero_serie):
    eleve = request.form['eleve'].strip()

    if not eleve:
        flash("Veuillez saisir le nom de l'élève.")
        return redirect(url_for('index'))

    # Séparer le nom et le prénom si possible
    parts = eleve.split(' ', 1)
    nom = parts[0].strip()
    prenom = parts[1].strip() if len(parts) > 1 else ""

    conn = get_db_connection()

    # Chercher l'étudiant existant
    etudiant = conn.execute(
        "SELECT id FROM etudiants WHERE nom = ? AND prenom = ?",
        (nom, prenom)
    ).fetchone()

    if etudiant is None:
        # Créer un étudiant temporaire
        cur = conn.execute("""
            INSERT INTO etudiants (nom, prenom, email, boursier, regime_scolarite)
            VALUES (?, ?, '', 0, 'inconnu')
        """, (nom, prenom))
        etudiant_id = cur.lastrowid
    else:
        etudiant_id = etudiant['id']

    # Créer le prêt avec cautions initialisées à 0
    conn.execute("""
        INSERT INTO prets (etudiant_id, ordinateur_id, caution_prof_validee, caution_compta_validee)
        VALUES (?, ?, 0, 0)
    """, (etudiant_id, numero_serie))

    # Marquer l'ordinateur comme emprunté
    conn.execute('UPDATE ordinateurs SET dispo = 0 WHERE numero_serie = ?', (numero_serie,))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

# Action : Rendre un PC
@app.route('/rendre/<path:numero_serie>', methods=('GET', 'POST'))
@login_required
def rendre(numero_serie):
    conn = get_db_connection()

    if request.method == 'POST':
        # Récupérer le commentaire obligatoire
        commentaire = request.form.get('commentaire')
        if not commentaire:
            conn.close()
            return "Erreur : vous devez renseigner un commentaire pour rendre l'ordinateur.", 400

        # Enregistrer le commentaire
        conn.execute(
            'INSERT INTO commentaires (ordinateur_id, commentaire, date_commentaire) VALUES (?, ?, CURRENT_DATE)',
            (numero_serie, commentaire)
        )

        # Récupérer le prêt actuel avec les infos de l'étudiant
        pret = conn.execute("""
            SELECT p.etudiant_id, e.nom, e.prenom, e.email, p.date_pret
            FROM prets p
            LEFT JOIN etudiants e ON p.etudiant_id = e.id
            WHERE p.ordinateur_id = ?
        """, (numero_serie,)).fetchone()

        # Si le prêt existe, l'enregistrer dans l'historique
        if pret:
            conn.execute("""
                INSERT INTO historique_prets (ordinateur_id, nom, prenom, email, date_pret, date_retour)
                VALUES (?, ?, ?, ?, ?, CURRENT_DATE)
            """, (numero_serie, pret['nom'], pret['prenom'], pret['email'], pret['date_pret']))

        # Supprimer le prêt en cours
        conn.execute("DELETE FROM prets WHERE ordinateur_id = ?", (numero_serie,))
        # Marquer comme disponible
        conn.execute('UPDATE ordinateurs SET dispo = 1 WHERE numero_serie = ?', (numero_serie,))

        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    # GET : afficher le formulaire de commentaire obligatoire
    conn.close()
    return render_template('commenter.html', numero_serie=numero_serie)
#la méthode ajouter n'est plus utilisé pour l'instant
@app.route('/ajouter', methods=['GET', 'POST'])
@login_required
def ajouter():
    if request.method == 'POST':
        id_pc = request.form.get('id_pc')
        modele_pc = request.form.get('modele_pc')
        date_sortie = request.form.get('date_sortie')

        if id_pc and modele_pc and date_sortie:
            conn = get_db_connection()
            try:
                conn.execute(
                    'INSERT INTO ordinateurs (id, modele, date_sortie) VALUES (?, ?, ?)',
                    (int(id_pc), modele_pc, date_sortie)
                )
                conn.commit()
            except sqlite3.IntegrityError:
                # Erreur si l'ID existe déjà
                conn.close()
                return "Erreur : l'ID existe déjà !", 400
            conn.close()
            return redirect(url_for('index'))
    return render_template('ajouter.html')
    
    
@app.route('/ajouter_modele', methods=['GET', 'POST'])
@login_required
def ajouter_modele():
    if request.method == 'POST':
        modele_pc = request.form.get('modele_pc')
        date_sortie = request.form.get('date_sortie')
        if modele_pc and date_sortie:
            # Récupérer le dernier modèle ajouté pour permettre d’ajouter les IDs
            return redirect(url_for('ajouter_pc_individuel', modele=modele_pc, date_sortie=date_sortie))
    return render_template('ajouter_modele.html')

@app.route('/ajouter_pc_individuel', methods=['GET', 'POST'])
@login_required
def ajouter_pc_individuel():
    if request.method == 'POST':
        numero_serie = request.form.get('numero_serie')
        numero_inventaire = request.form.get('numero_inventaire')
        modele_pc = request.form.get('modele_pc')
        date_sortie = request.form.get('date_sortie')
        #date_sortie = request.form.get('date_sortie')

        if numero_inventaire and modele_pc and date_sortie and numero_serie:
            conn = get_db_connection()
            try:
                conn.execute(
                    'INSERT INTO ordinateurs (numero_serie, numero_inventaire, modele, date_sortie) VALUES (?, ?, ?,?)',
                    (numero_serie, numero_inventaire, modele_pc, date_sortie)
                )
                conn.commit()
            except sqlite3.IntegrityError:
                conn.close()
                return "Erreur : l'ID existe déjà !", 400
            conn.close()
            # Rediriger vers le même formulaire pour ajouter d’autres PC du même modèle
            return redirect(url_for('ajouter_pc_individuel', modele=modele_pc, date_sortie=date_sortie))
    else:
        # GET : récupérer le modèle passé en query string
        modele_pc = request.args.get('modele')
        date_sortie = request.args.get('date_sortie')
        return render_template('ajouter_pc_individuel.html', modele=modele_pc, date_sortie=date_sortie)

#-----

# Programmation de l'envoye de mails

@app.route("/mail")
@login_required
def mail():
    return render_template("mail.html")

@app.route("/mail", methods=["GET", "POST"])
@login_required
def programmation_mails():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if request.method == "POST":

        cible = request.form["cible"]
        objet = request.form["objet"]
        contenu = request.form["contenu"]
        date_envoi = request.form["date_envoi"]

        # mapping entre le select HTML et les id de la table
        mapping = {
            "retard": 1,
            "tous": 2,
            "boursiers": 3
        }

        cible_id = mapping[cible]

        cur.execute("""
            INSERT INTO mails (cible_id, objet, contenu, date_envoi)
            VALUES (?, ?, ?, ?)
        """, (cible_id, objet, contenu, date_envoi))

        conn.commit()

    # mails programmés (envoye = 0)
    cur.execute("""
        SELECT mails.id, mails.objet, mails.date_envoi, cibles_mails.cible
        FROM mails
        JOIN cibles_mails ON mails.cible_id = cibles_mails.id
        WHERE mails.envoye = 0
    """)
    mails_programmes = cur.fetchall()

    # mails envoyés (envoye = 1)
    cur.execute("""
        SELECT mails.id, mails.objet, mails.date_envoi, cibles_mails.cible
        FROM mails
        JOIN cibles_mails ON mails.cible_id = cibles_mails.id
        WHERE mails.envoye = 1
    """)
    mails_envoyes = cur.fetchall()

    conn.close()

    return render_template(
        "mail.html",
        mails_programmes=mails_programmes,
        mails_envoyes=mails_envoyes
    )

@app.route("/mail/supprimer/<int:id>")
@login_required
def supprimer_mail(id):

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute("DELETE FROM mails WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("programmation_mails"))

@app.route("/mail/modifier/<int:id>", methods=["GET", "POST"])
@login_required
def modifier_mail(id):

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if request.method == "POST":
        objet = request.form["objet"]
        contenu = request.form["contenu"]
        date_envoi = request.form["date_envoi"]

        cur.execute("""
            UPDATE mails
            SET objet = ?, contenu = ?, date_envoi = ?
            WHERE id = ?
        """, (objet, contenu, date_envoi, id))

        conn.commit()
        conn.close()

        return redirect(url_for("programmation_mails"))

    cur.execute("SELECT * FROM mails WHERE id = ?", (id,))
    mail = cur.fetchone()

    conn.close()

    return render_template("modifier_mail.html", mail=mail)

# Update de la table des étudiants à partir des nouveaux .csv

@app.route("/update_etudiants", methods=["GET", "POST"])
@login_required
def update_etudiants():
    if request.method == "POST":
        uploaded_files = request.files.getlist("files")
        # On prend jusqu'à 4 fichiers
        
        file1 = uploaded_files[0] if len(uploaded_files) > 0 else None
        file2 = uploaded_files[1] if len(uploaded_files) > 1 else None
        file3 = uploaded_files[2] if len(uploaded_files) > 2 else None
        file4 = uploaded_files[3] if len(uploaded_files) > 3 else None

        process_etudiants(file1, file2, file3, file4)

        flash("Les étudiants ont été mis à jour avec succès.")

        return redirect(url_for("index"))

    return render_template("update_etudiants.html")

# Modification de la convention

@app.route("/convention")
@login_required
def modification_convention():
    return render_template("modifier_convention.html")

@app.route("/convention/download")
@login_required
def telecharger_convention():

    chemin = os.path.join(app.root_path, "Convention", "convention.tex")

    return send_file(
        chemin,
        as_attachment=True,
        download_name="convention.tex"
    )

@app.route("/convention/upload", methods=["POST"])
@login_required
def upload_convention():

    file = request.files.get("file_tex")

    if file and file.filename.endswith(".tex"):
        chemin = os.path.join(app.root_path, "Convention" ,"convention.tex")
        file.save(chemin)

    return redirect(url_for("modification_convention"))

# Génération de la convention pour un élève

@app.route('/convention/generation', methods=['GET', 'POST'])
@login_required
def generation_convention():
    if request.method == 'POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        observation = request.form.get('observation')
        signature = request.form.get('signature')

        # Vérification minimale
        if not nom or not prenom:
            flash("Nom et prénom sont obligatoires.")
            return redirect(url_for('generation_convention'))

        conn = get_db_connection()

        # Vérifier si l'étudiant existe
        etudiant = conn.execute(
            "SELECT * FROM etudiants WHERE nom = ? AND prenom = ?",
            (nom, prenom)
        ).fetchone()

        ordinateur = conn.execute(
            "SELECT * FROM ordinateurs WHERE dispo = 1 LIMIT 1"
        ).fetchone()

        if ordinateur is None:
            flash("Aucun ordinateur disponible.")
            conn.close()
            return redirect(url_for('generation_convention'))

        modele = ordinateur["modele"]
        numero_inventaire = ordinateur["numero_inventaire"]
        numero_serie = ordinateur["numero_serie"]

        conn.execute(
            "UPDATE ordinateurs SET dispo = 0 WHERE numero_serie = ?",
            (numero_serie,)
        )

        conn.commit()
        conn.close()        

        if etudiant is None:
            flash("Cet étudiant n'existe pas dans la base.")
            return redirect(url_for('generation_convention'))

        # récupération des champs de la base
        annee_etude = etudiant["annee"]
        ine = etudiant["ine"]

        generer_convention(
            nom,
            prenom,
            annee_etude,
            ine,
            observation,
            modele,
            numero_inventaire,
            numero_serie
        )

        return redirect(url_for('index'))

    return render_template('convention_generation.html')

#-----

@app.route('/supprimer/<path:numero_serie>', methods=['POST'])
@login_required
def supprimer(numero_serie):
    conn = get_db_connection()

    # Vérifier si l'ordinateur est emprunté
    pret = conn.execute("SELECT * FROM prets WHERE ordinateur_id = ?", (numero_serie,)).fetchone()
    if pret:
        conn.close()
        return "Erreur : impossible de supprimer un ordinateur en prêt !", 400

    # Sinon, supprimer l'ordinateur
    conn.execute("DELETE FROM ordinateurs WHERE numero_serie = ?", (numero_serie,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))
    
@app.route('/valider-caution-prof/<numero_serie>', methods=['POST'])
@login_required
def valider_caution_prof(numero_serie):
    conn = get_db_connection()

    conn.execute("""
        UPDATE prets
        SET caution_prof_validee = 1
        WHERE ordinateur_id = ? AND date_retour > CURRENT_DATE
    """, (numero_serie,))

    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/valider-caution-compta/<numero_serie>', methods=['POST'])
@login_required
def valider_caution_compta(numero_serie):
    conn = get_db_connection()

    # sécurité : on ne valide que si le prof a validé
    conn.execute("""
        UPDATE prets
        SET caution_compta_validee = 1
        WHERE ordinateur_id = ?
          AND caution_prof_validee = 1 AND date_retour > CURRENT_DATE
    """, (numero_serie,))

    conn.commit()
    conn.close()

    return redirect(url_for('index'))
    
@app.route('/envoyer-reparation/<path:numero_serie>', methods=['POST'])
@login_required
def envoyer_reparation(numero_serie):
    conn = get_db_connection()
    conn.execute('UPDATE ordinateurs SET dispo = 2 WHERE numero_serie = ?', (numero_serie,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/reparation-terminee/<path:numero_serie>', methods=['POST'])
@login_required
def reparation_terminee(numero_serie):
    conn = get_db_connection()
    conn.execute('UPDATE ordinateurs SET dispo = 1 WHERE numero_serie = ?', (numero_serie,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/ajouter_commentaire/<path:numero_serie>', methods=['POST'])
@login_required
def ajouter_commentaire(numero_serie):
    commentaire = request.form.get('commentaire')
    if commentaire:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO commentaires (ordinateur_id, commentaire, date_commentaire) VALUES (?, ?, CURRENT_DATE)',
            (numero_serie, commentaire)
        )
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, ssl_context='adhoc') #permet de générer un certificat https temporaire.
