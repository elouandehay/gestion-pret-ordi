DROP TABLE IF EXISTS prets;
DROP TABLE IF EXISTS commentaires;
DROP TABLE IF EXISTS ordinateurs;
DROP TABLE IF EXISTS etudiants;
DROP TABLE IF EXISTS administrateurs;

-- Table Administrateurs
CREATE TABLE administrateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

-- Table Ordinateurs
CREATE TABLE ordinateurs (
    numero_serie TEXT PRIMARY KEY,
    numero_inventaire TEXT NOT NULL,
    date_sortie DATE NOT NULL,
    modele TEXT NOT NULL,
    dispo INTEGER DEFAULT 1
);

-- Les autres tables que tu veux garder (inchangées)
CREATE TABLE etudiants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_apprenant INTEGER,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    email TEXT NOT NULL,
    email_insa TEXT,
    boursier BOOL NOT NULL,
    ine TEXT,
    regime_scolarite TEXT NOT NULL,
    annee INTEGER DEFAULT NULL,
    en_scolarite BOOL DEFAULT 1
);

CREATE TABLE prets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caution_prof_validee INTEGER DEFAULT 0,
    caution_compta_validee INTEGER DEFAULT 0,
    etudiant_id INTEGER NOT NULL,
    ordinateur_id TEXT NOT NULL,
    date_pret DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_retour DATETIME DEFAULT (DATETIME('now', '+1095 days')), -- 3 ans
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (ordinateur_id) REFERENCES ordinateurs(numero_serie)
);

CREATE TABLE commentaires (
   ordinateur_id TEXT,
   commentaire TEXT,
   date_commentaire DATE DEFAULT CURRENT_DATE,
   FOREIGN KEY (ordinateur_id) REFERENCES ordinateurs(numero_serie)
   );
