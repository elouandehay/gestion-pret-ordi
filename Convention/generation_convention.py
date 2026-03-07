from jinja2 import Environment, FileSystemLoader
from datetime import date
import subprocess
import os


def generer_convention(nom, prenom, annee_etude, ine, observation):
    jour = date.today().strftime("%d/%m/%Y")

    # Chargement du template
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('Convention/convention.tex')

    # Rendu avec les variables
    output = template.render(
        nom=nom,
        prenom=prenom,
        annee_etude=str(annee_etude),
        date=jour,
        ine=str(ine),
        obs=observation
    )

    # Nom du fichier basé sur l'INE
    filename = f"convention_{ine}.tex"

    # Écriture du fichier
    with open(filename, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"Fichier {filename} généré.")
 
    # Compilation LaTeX -> PDF
    result = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", filename],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    print(result.stderr)
    print(result.stdout)

    pdf_file = f"convention_{ine}.pdf"

    if os.path.exists(pdf_file):
        print(f"{pdf_file} généré avec succès.")
        return pdf_file
    else:
        print("Erreur lors de la génération du PDF.")
        return None 

