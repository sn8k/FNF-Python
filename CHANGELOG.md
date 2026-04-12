# Changelog

## 2026-04-12
- mise en place d'un systeme de logs central configurable via `data/config.json`
- ajout de deux canaux de logs distincts : `user` et `debug`
- migration des sorties `print()` principales vers le systeme de logs dans `main.py`, `setup_check.py` et les modules `src/`
- ajout d'une documentation projet minimale sur la politique de logs dans `DOCS/`
- note de verification : la date `2026-04-12` a ete verifiee localement via la commande systeme
- note de verification : l'etat Git n'a pas pu etre verifie dans cet environnement car `git` n'etait pas disponible
