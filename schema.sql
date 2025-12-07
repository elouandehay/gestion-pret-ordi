DROP TABLE IF EXISTS ordinateurs;
DROP TABLE IF EXISTS etudiants;
DROP TABLE IF EXISTS prets;
DROP TABLE IF EXISTS commentaires;


CREATE TABLE etudiants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    prenom TEXT NOT NULL,
    email TEXT NOT NULL,
    boursier BOOL NOT NULL
);
CREATE TABLE ordinateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_sortie DATE NOT NULL,
    modele TEXT NOT NULL,
    dispo INTEGER DEFAULT 1
);

CREATE TABLE prets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    etudiant_id INTEGER NOT NULL,
    ordinateur_id INTEGER NOT NULL,
    date_pret DATETIME DEFAULT CURRENT_TIMESTAMP,
    date_retour DATETIME DEFAULT (DATETIME('now', '+1095 days')), -- 3 ans
    FOREIGN KEY (etudiant_id) REFERENCES etudiants(id),
    FOREIGN KEY (ordinateur_id) REFERENCES ordinateurs(id)
);

CREATE TABLE commentaires (
   ordinateur_id INTEGER,
   commentaire TEXT,
   date_commentaire DATE NOT NULL,
   FOREIGN KEY (ordinateur_id) REFERENCES ordinateurs(id)
   );
  
CREATE TABLE compte (
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   nom_utilisateur TEXT NOT NULL,
   mdp_hashage TEXT NOT NULL
   );

-- On insère quelques PC pour tester
INSERT INTO ordinateurs (nom, etat) VALUES ('PC-001', 'disponible');
INSERT INTO ordinateurs (nom, etat) VALUES ('PC-002', 'disponible');

-- CORRECTION ICI : J'ai ajouté ", emprunteur" dans la parenthèse
INSERT INTO ordinateurs (nom, etat, emprunteur) VALUES ('PC-003', 'emprunte', 'Jean Dupont');
