# Bot Feur

[![Python 3.10.8](https://img.shields.io/badge/python-3.10.8-blue.svg)](https://www.python.org/downloads/release/python-3108/)

Un bot qui réagit aux utilisateurs de Discord qui ont le malheur de dire "Quoi" !

## Fonctionnalités

### Réactions

- Réagit avec une émote <img src="emotes/feur.png" width="30" height="30"/> quand un utilisateur dit "Quoi" dans un salon écrit.

- Réagit avec les émotes <img src="emotes/al.png" width="30" height="30"/> <img src="emotes/huile.png" width="30" height="30"/> quand un utilisateur dit "Allo" dans un salon écrit.

La reconnaissance des mots interdits est basée sur [epitran](https://pypi.org/project/epitran/), une bibliothèque permettant de convertir du texte en sa prononciation dans de nombreuses langues

### Commandes

- `/rankfeur` : Affiche le classement des utilisateurs qui ont le plus dit "Quoi".

- `/nbfeur @user` : Affiche le nombre de fois où le bot a réagi à "Quoi" pour un utilisateur (par défaut, l'utilisateur qui a envoyé la commande).

- `/memegen image (top) (bottom)` : Génère une image avec le texte en haut et en bas. L'image doit être donnée sous forme d'un lien. Les deux textes sont optionnels.
