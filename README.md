# Erreurs possibles dans le `app.py`

## Route /emprunter
  
- Il faut vérifier que l'étudiant est déjà référencé dans la table pour lui 
  accordé un prêt.
Ou :
- Manuellement référencer toutes les informations de l'étudiant pour avoir son 
  instance complête dans la table.
  **Rq :** Cela suppose que les fichiers .csv soit entièrement constitué et non
  sujet à être modifié avant l'attribution d'un prêt. (Sinon il faudra 
  Réuploder chaque ficher juste pour l'étudiant manquant)

## Route /rendre

- On supprime le prêt de la table des prêts au moment on l'on estime que 
  l'ordinateur est rendu **or** il y a une date de début et de fin ce qui
  suppose de conserver l'historique des prêts même ceux qui ne sont plus
  en cours.
  **Rq :** Même si il est vrai qu'il est légitime de mettre un commentaire
  hors prêt (par exemple avant ou après une réparation) il pourrait être 
  souhaitable de mettre pour les commentaires concerner une foreign key
  vers un prêt. Aussi il pourrait être souhaitable de mettre un champ 
  determinant la nature du commentaire style :
    -> début de prêt
    -> fin de prêt
    -> avant réparation
    -> après réparation
    -> hors prêt ...

- A chaque fois que l'on rend l'ordi on supprime le prêt mais le champ id est
  en auto-incrementation (=> il y aura des trou dans les id si on ne décremente
  pas). De plus l'implémentation en auto-incrementation suppose justement dans
  ce cas que l'on tient à conserver les prêts non en cours dans la base.
