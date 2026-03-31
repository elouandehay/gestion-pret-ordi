# Dans app.py
from apscheduler.schedulers.background import BackgroundScheduler
import yagmail
from datetime import datetime
import sqlite3

# Récupère les emails des étudiants avec prêt actif ---
def recuperer_emails():
    db_file = "database.db"
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Récupère les id des étudiants avec un prêt actif
    cur.execute("""
        SELECT DISTINCT etudiant_id
        FROM prets
        WHERE date_retour > CURRENT_TIMESTAMP
    """)
    etudiants_ids = [row["etudiant_id"] for row in cur.fetchall()]

    emails_perso = []
    emails_insa = []

    if etudiants_ids:
        placeholders = ",".join("?" for _ in etudiants_ids)
        cur.execute(f"""
            SELECT email, email_insa
            FROM etudiants
            WHERE id IN ({placeholders})
        """, etudiants_ids)
        for row in cur.fetchall():
            emails_perso.append(row["email"])
            emails_insa.append(row["email_insa"])

    conn.close()
    return emails_perso, emails_insa

# --- Fonction pour envoyer les mails ---
def envoyer_mails_etudiants():
    emails_perso, emails_insa = recuperer_emails()

    # config Yagmail avec ton compte Gmail / SMTP
    # attention, tu dois créer un mot de passe spécifique si 2FA activé
    yag = yagmail.SMTP(user="ton_email@gmail.com", password="ton_mot_de_passe")

    sujet = "Rappel matériel informatique"
    contenu = """
        Bonjour,

        Ceci est un rappel pour les étudiants n'ayant pas rendu ou ayant emprunté du matériel informatique.

        Merci de régulariser votre situation rapidement.
        """

    # envoyer à tous les mails perso
    for mail in emails_perso:
        if mail:  # ignore les emails vides
            yag.send(to=mail, subject=sujet, contents=contenu)

    # envoyer à tous les mails INSA
    for mail in emails_insa:
        if mail:
            yag.send(to=mail, subject=sujet, contents=contenu)

    print(f"[{datetime.now()}] Mails envoyés à {len(emails_perso)+len(emails_insa)} étudiants.")

# --- Route Flask pour déclenchement manuel ---
@app.route("/envoyer_mails")
@login_required
def route_envoyer_mails():
    try:
        envoyer_mails_etudiants()
        return "✅ Mails envoyés avec succès !"
    except Exception as e:
        return f"❌ Erreur lors de l'envoi des mails : {e}"

# --- Supposons que tu veuilles envoyer les mails le 15 mars 2026 à 18h30 ---
date_envoi = datetime(2026, 3, 15, 18, 30, 0)  # année, mois, jour, heure, minute, seconde

scheduler = BackgroundScheduler()
scheduler.add_job(envoyer_mails_etudiants, 'date', run_date=date_envoi)
scheduler.start()

print(f"[{datetime.now()}] Mail programmé pour le {date_envoi}")
