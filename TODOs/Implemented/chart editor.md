Feature request pour le chart editor : 
  - Selectionner qui est contre qui (VERSUS) dans les fichiers 'characters' , choisir la musique, placer / supprimer des notes, exporter ce fichier en fichier .json pour pouvoir y jouer dans fnf (source : https://github.com/ShadowMario/FNF-PsychEngine) ou ce jeu meme.

Implementation 2026-04-12 :
- `TAB` et `SHIFT+TAB` selectionnent la musique de preview et remplissent le champ `audio`.
- `P` selectionne le prochain dossier de personnage joueur.
- `O` selectionne le prochain dossier de personnage ennemi.
- Clic gauche et clic droit gardent l'ajout/suppression des notes.
- `CTRL+S` exporte un JSON natif jouable dans `data/charts/`, avec `name`, `bpm`, `offset`, `notes`, `audio`, `player` et `enemy`.
