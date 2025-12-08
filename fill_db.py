import csv
import re
from app import app
from model import db, Etudiant

FICHIER = "suivi_inscriptions_202511271311.csv"

# regex : département qui se termine par "INFO"
regex_info = re.compile(r"INFO$", re.IGNORECASE)

def increment_annee(annee):
    if annee < 5:
        return annee + 1
    return 5

def convert_bourse(valeur): 

    return valeur.strip().lower() in ["oui", "yes", "true", "1"]


with app.app_context():

    # 1) Incrémenter l’année ou reset en_scolarite
    etudiants = Etudiant.query.all()
    for etu in etudiants:

        if etu.annee = 5:
            etu.en_scolarite = False
            continue

        etu.annee = increment_annee(etu.annee)
 

    db.session.commit()

    # 2) Lecture du CSV et mise à jour
    with open(FICHIER, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')

        for ligne in reader:

            # --- Filtrage par département             
            departement = ligne.get("Département", "")

            if not regex_info.search(departement):
                # On ignore cet étudiant
                continue

            id_ine = ligne["N°INE"]

            # Conversion du champ boursier
            boursier = convert_bourse(ligne["Témoin bourse"])

            etu = Etudiant.query.get(id_ine)

            if etu is None:
                # Ajout
                etu = Etudiant(
                    id=id_ine,
                    nom=ligne["Nom"],
                    prenom=ligne["Prénom"],
                    email=ligne["Email"],
                    boursier=boursier,
                    annee=3,  # année par défaut d'entrée
                    en_scolarite=True
                )
                db.session.add(etu)

            else:
                # Mise à jour
                etu.nom = ligne["Nom"]
                etu.prenom = ligne["Prénom"]
                etu.email = ligne["Email"]
                etu.boursier = boursier  

    db.session.commit()
