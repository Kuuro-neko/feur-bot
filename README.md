# Bot Feur

[![Python 3.10.8](https://img.shields.io/badge/python-3.10.8-blue.svg)](https://www.python.org/downloads/release/python-3108/)

Un bot qui réagit aux utilisateurs de Discord qui ont le malheur de dire "Quoi" !

## Fonctionnalités

### Réactions

- Réagit avec une émote ![feur]('emotes/feur.png') quand un utilisateur dit "Quoi" dans un salon écrit.

- Réagit avec les émotes ![al]('emotes/al.png') ![huile]('emotes/huile.png') quand un utilisateur dit "Allo" dans un salon écrit.

### Commandes

- `/rankfeur` : Affiche le classement des utilisateurs qui ont le plus dit "Quoi".

- `/nbfeur @user` : Affiche le nombre de fois où le bot a réagi à "Quoi" pour un utilisateur (par défaut, l'utilisateur qui a envoyé la commande).

- `/memegen image top(opt) bottom(opt)` : Génère une image avec le texte en haut et en bas. L'image doit être donnée sous forme d'un lien. Les deux textes sont optionnels.