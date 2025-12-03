import csv
from app import app
from model import db, Etudiant

FICHIER = "suivi_inscriptions_202511271311.csv"

with app.app_context():  # pour accéder à la DB dans un script externe
    with open(FICHIER, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')

        for ligne in reader:
            etu = Etudiant(
                # manque boursier : true/false
                id=ligne["N°INE"],
                nom=ligne["Nom"],
                prenom=ligne["Prénom"],
                email=ligne["Email"],
                annee=1  # ou autre valeur par défaut
                # manque pret
            )

            db.session.add(etu)

        db.session.commit()

