import csv
from app import app
from model import db, Etudiant

FICHIER = "suivi_inscriptions_202511271311.csv"

def increment_annee(annee):
    if annee < 5:
        return annee + 1
    return 5


with app.app_context():
 
    # 1) Incrémenter l’année de tous les étudiants
    etudiants = Etudiant.query.all()
    for etu in etudiants:
        etu.annee = increment_annee(etu.annee)
        etu.en_scolarite = False 

    db.session.commit()
    
    # 2) Lecture du CSV et mise à jour
    with open(FICHIER, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')

        for ligne in reader:
            id_ine = ligne["N°INE"]

            etu = Etudiant.query.get(id_ine)

            if etu is None:
                # Étudiant inexistant → ajout
                etu = Etudiant(
                    id=id_ine,
                    nom=ligne["Nom"],
                    prenom=ligne["Prénom"],
                    email=ligne["Email"],
                    annee=3,  # année d'entrée, modifiable selon tes règles
                    en_scolarite=True
                )
                db.session.add(etu)
            else:
                # Étudiant existant → update
                etu.nom = ligne["Nom"]
                etu.prenom = ligne["Prénom"]
                etu.email = ligne["Email"] 
                etu.en_scolarite = True
                
    db.session.commit() 
