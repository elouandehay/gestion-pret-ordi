from jinja2 import Environment, FileSystemLoader
from datetime import date
import subprocess
import os

def generer_convention(nom, prenom, annee_etude, ine, observation, modele, numero_inventaire, numero_serie):

    jour = date.today().strftime("%d/%m/%Y")

    base_dir = "Convention/conventions_generees"
    convention_dir = os.path.join(base_dir, f"convention_{ine}")

    os.makedirs(convention_dir, exist_ok=True)

    # Chargement du template
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('Convention/convention.tex')

    output = template.render(
        nom=nom,
        prenom=prenom,
        annee_etude=str(annee_etude),
        date=jour,
        ine=str(ine),
        obs=observation,
        modele=modele,
        numero_inventaire=numero_inventaire,
        numero_serie=numero_serie
    )

    tex_file = os.path.join(convention_dir, f"convention_{ine}.tex")

    with open(tex_file, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"Fichier {tex_file} généré.")

    # Compilation LaTeX dans le dossier de la convention
    result = subprocess.run(
        [
            "pdflatex",
            "-interaction=nonstopmode",
            "-output-directory",
            convention_dir,
            tex_file
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore"
    )

    print(result.stderr)
    print(result.stdout)

    pdf_file = os.path.join(convention_dir, f"convention_{ine}.pdf")

    if os.path.exists(pdf_file):
        print(f"{pdf_file} généré avec succès.")
        return pdf_file
    else:
        print("Erreur lors de la génération du PDF.")
        return None
