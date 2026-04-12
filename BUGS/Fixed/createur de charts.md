Bug constaté :
le createur de charts n'est pas fonctionnel, celui ci ne s'execute meme pas.
A diagnostiquer et rendre fonctionnel.

Resolution 2026-04-12 :
- verification compilation : `python -m py_compile main.py setup_check.py src/__init__.py src/chart_editor.py src/game.py src/logging_utils.py src/menu.py src/resources.py src/settings.py src/sprites.py src/week_editor.py src/week_manager.py`
- verification headless : instanciation de `ChartEditor` avec `SDL_VIDEODRIVER=dummy` et `SDL_AUDIODRIVER=dummy`
- resultat : l'editeur de charts s'initialise correctement dans l'etat courant du code
