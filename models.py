from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()

class Administrateur(db.Model):
    __tablename__ = "administrateurs"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)

class Ordinateur(db.Model):
    __tablename__ = "ordinateurs"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(255), nullable=False)
    etat = db.Column(db.String(255), nullable=False)
    emprunteur = db.Column(db.String(255))  # Peut être NULL

    # Relation avec les prêts
    prets = db.relationship("Pret", backref="ordinateur", lazy=True)

class Etudiant(db.Model):
    __tablename__ = "etudiants"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    boursier = db.Column(db.Boolean, nullable=False)
    en_scolarite = db.Column(db.Boolean, nullable=False, default=False)
    prets = db.relationship("Pret", backref="etudiant", lazy=True)

class Pret(db.Model):
    __tablename__ = "prets"

    id = db.Column(db.Integer, primary_key=True)
    etudiant_id = db.Column(
        db.Integer,
        db.ForeignKey("etudiants.id"),
        nullable=False
    )

    ordinateur_id = db.Column(db.Integer, db.ForeignKey("ordinateurs.id"), nullable=False)
    date_pret = db.Column(db.DateTime, default=datetime.now, nullable=False)
    # Défaut : + 3 ans
    date_retour = db.Column(db.DateTime, default=lambda: datetime.now() + timedelta(days=3 * 365), nullable=False)

class Commentaire(db.Model):
    __tablename__ = "commentaires"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ordinateur_id = db.Column(db.Integer, db.ForeignKey("ordinateurs.id"))
    commentaire = db.Column(db.Text)
    date_commentaire = db.Column(db.Date, nullable=False)
    ordinateur = db.relationship("Ordinateur", backref="commentaires", lazy=True)
