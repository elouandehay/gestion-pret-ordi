# update_etudiants.py

import sqlite3
import csv


def process_etudiants(registration_file, info3_file=None, info4_file=None, info5_file=None, db_file="database.db"):
    """
    Met à jour la base des étudiants à partir des CSV fournis.
    Les fichiers sont des objets FileStorage envoyés par Flask.
    """

    if not registration_file:
        raise ValueError("Le fichier principal d'inscription est obligatoire.")

    etudiants_en_scolarite = []

    regime_inscription_ok = {
        "IRE-ING-3INF": 3,
        "IRE-ING-4INF": 4,
        "IRE-ING-5INF": 5
    }

    conn = sqlite3.connect(db_file)
    cur = conn.cursor()

    # ---------- 1. Lecture du fichier principal ----------
    registration_file.stream.seek(0)

    reader = csv.DictReader(
        (line.decode("utf-8-sig") for line in registration_file.stream),
        delimiter=";"
    )

    id_counter = 0

    for row in reader:

        nom = row.get("Nom")
        prenom = row.get("Prénom")
        ine = row.get("N°INE")
        email = row.get("Email")
        # On convertit en 1 si le texte est "Oui", "O", "1" ou "True"
        raw_boursier = str(row.get("Témoin bourse", "")).strip().lower()
        boursier = 1 if raw_boursier in ['oui', 'o', '1', 'true'] else 0
        regime_inscription = row.get("Régime Inscription")
        code_apprenant = row.get("Code Apprenant")

        if regime_inscription not in regime_inscription_ok:
            continue

        annee = regime_inscription_ok[regime_inscription]
        etudiants_en_scolarite.append((nom, prenom))
        id_counter += 1

        cur.execute(
            "SELECT id FROM etudiants WHERE nom=? AND prenom=?",
            (nom, prenom)
        )
        result = cur.fetchone()

        if result:
            cur.execute(
                """
                UPDATE etudiants
                SET code_apprenant=?,
                    email=?,
                    boursier=?,
                    ine=?,
                    regime_scolarite=?,
                    annee=?,
                    en_scolarite=?
                WHERE nom=? AND prenom=?
                """,
                (code_apprenant, email, boursier, ine, regime_inscription, annee, 1, nom, prenom)
            )
        else:
            cur.execute(
                """
                INSERT INTO etudiants (
                    id, nom, prenom, email, boursier,
                    ine, regime_scolarite, annee,
                    en_scolarite, code_apprenant
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (id_counter, nom, prenom, email, boursier,
                 ine, regime_inscription, annee,
                 1, code_apprenant)
            )

    conn.commit()

    # ---------- 2. Mise à jour des emails INSA ----------
    for info_file in [info3_file, info4_file, info5_file]:

        if not info_file:
            continue

        info_file.stream.seek(0)

        reader = csv.DictReader(
            (line.decode("utf-8-sig") for line in info_file.stream),
            delimiter=",",
            quotechar='"'
        )

        if reader.fieldnames:
            reader.fieldnames = [h.strip().replace('\ufeff', '') for h in reader.fieldnames]

        for row in reader:

            nom = row.get("Nom")
            prenom = row.get("Prénom")
            email_insa = row.get("Email")

            if nom and prenom and email_insa:
                cur.execute(
                    """
                    UPDATE etudiants
                    SET email_insa=?
                    WHERE nom=? AND prenom=?
                    """,
                    (email_insa, nom, prenom)
                )

        conn.commit()

    # ---------- 3. Étudiants plus en scolarité ----------
    cur.execute("SELECT nom, prenom FROM etudiants")
    etudiants_db = cur.fetchall()

    for nom, prenom in etudiants_db:

        if (nom, prenom) not in etudiants_en_scolarite:
            cur.execute(
                """
                UPDATE etudiants
                SET en_scolarite="non",
                    annee=NULL
                WHERE nom=? AND prenom=?
                """,
                (nom, prenom)
            )

    conn.commit()
    conn.close()
