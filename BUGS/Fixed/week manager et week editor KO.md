week manager et week editor ne se lancent pas.

Resolution 2026-04-12 :
- verification CLI : `python -m src.week_manager`
- verification headless : instanciation de `WeekEditor` avec `SDL_VIDEODRIVER=dummy` et `SDL_AUDIODRIVER=dummy`
- resultat : le week manager liste les weeks/charts et l'editeur de weeks s'initialise correctement dans l'etat courant du code
