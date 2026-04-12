# Journal de connaissances

## 2026-04-12
- piege : le projet utilisait des `print()` disperses dans plusieurs modules, sans separation claire entre messages utilisateur et details techniques
- correction : ajout d'un module central `src/logging_utils.py` avec deux familles de loggers, `user` et `debug`
- piege : `data/config.json` n'avait aucune reference pour piloter les logs
- correction : ajout d'un bloc `logging` dans `data/config.json`
- piege : l'etat Git n'est pas verifiable dans cet environnement car la commande `git` est indisponible
- consequence : ne pas inventer de revision ou de commit dans la documentation de travail
