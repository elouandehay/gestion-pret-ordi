from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()
class Etudiant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    prets = db.relationship("Pret", backref="etudiant", lazy=True)

class Ordinateur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    modele = db.Column(db.String(100), nullable=False)
    dispo = db.Column(db.Boolean, default=True)
    prets = db.relationship("Pret", backref="ordinateur", lazy=True)

class Pret(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(db.Integer, db.ForeignKey("etudiant.id"), nullable=False)
    ordinateur_id = db.Column(db.Integer, db.ForeignKey("ordinateur.id"), nullable=False)
    date_pret = db.Column(db.DateTime, default=datetime.now(), nullable=False)
    #date retour : valeur par défaut = 3 ans après date_pret
    date_retour = db.Column(db.DateTime, default=lambda: datetime.now() + timedelta(days=3*365), nullable=False)