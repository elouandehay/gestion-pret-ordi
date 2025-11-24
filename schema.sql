DROP TABLE IF EXISTS ordinateurs;

CREATE TABLE ordinateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    etat TEXT NOT NULL DEFAULT 'disponible', -- 'disponible' ou 'emprunte'
    emprunteur TEXT -- Nom de l'élève si emprunté
);

-- On insère quelques PC pour tester
INSERT INTO ordinateurs (nom, etat) VALUES ('PC-001', 'disponible');
INSERT INTO ordinateurs (nom, etat) VALUES ('PC-002', 'disponible');

-- CORRECTION ICI : J'ai ajouté ", emprunteur" dans la parenthèse
INSERT INTO ordinateurs (nom, etat, emprunteur) VALUES ('PC-003', 'emprunte', 'Jean Dupont');
