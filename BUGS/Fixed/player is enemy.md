le personnage joué par l'utilisateur devrait etre le personnage de droite, et non celui de gauche.

Correction 2026-04-12 :
- Le joueur reste instancie a droite dans `Game.setup_sprites()`.
- Les hits reussis animent maintenant `self.player` au lieu de `self.opponent`.
- Les champs optionnels `player` et `enemy` permettent de choisir explicitement les dossiers de personnages du chart.
