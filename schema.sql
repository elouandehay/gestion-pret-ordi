DROP TABLE IF EXISTS ordinateurs;
DROP TABLE IF EXISTS etudiants;
DROP TABLE IF EXISTS prets;
DROP TABLE IF EXISTS commentaires;
DROP TABLE IF EXISTS administrateurs;

-- Table Administrateurs (ESSENTIELLE pour le login)
CREATE TABLE administrateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

-- Table Ordinateurs (MODIFIÉE pour correspondre à ton app.py et aux INSERTs)
CREATE TABLE ordinateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    etat TEXT NOT NULL,
    emprunteur TEXT
);

-- Les autres tables que tu veux garder (inchangées)
CREATE TABLE etudiants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    email TEXT NOT NULL,
    boursier BOOL NOT NULL
);

CREATE TABLE prets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    ordinateur_id INTEGER NOT NULL,
    date_pret DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_retour DATETIME DEFAULT (DATETIME('now', '+1095 days')),
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (ordinateur_id) REFERENCES ordinateurs(id)
);

CREATE TABLE commentaires (
   ordinateur_id INTEGER,
   commentaire TEXT,
   date_commentaire DATE NOT NULL,
   FOREIGN KEY (ordinateur_id) REFERENCES ordinateurs(id)
);

-- INSERTION DES DONNÉES (Cela fonctionnera maintenant)
INSERT INTO ordinateurs (nom, etat) VALUES ('PC-001', 'disponible');
INSERT INTO ordinateurs (nom, etat) VALUES ('PC-002', 'disponible');
INSERT INTO ordinateurs (nom, etat, emprunteur) VALUES ('PC-003', 'emprunte', 'Jean Dupont');
