# Backlog - Pause ingame et menu pause

Date de creation verifiee: 2026-04-12

## Regles de suivi
- [x] L'agent responsable de cette TODO maintient ce fichier a jour a chaque livraison partielle en cochant uniquement les taches effectivement en place.
- [x] Le backlog est deplace vers `TODOs/Implemented/` uniquement quand toutes les cases sont cochees et que les verifications finales sont passees.

## Criteres d'acceptation
- [x] `ESC` en partie ouvre un menu pause au lieu de quitter directement la partie.
- [x] `reprendre` ferme la pause et reprend exactement la partie courante.
- [x] `options` ouvre les options existantes en contexte ingame puis revient au menu pause.
- [x] `restart` relance le chart courant depuis zero avec un etat propre.
- [x] `quit` arrete la partie en cours et revient au menu principal.

## Agent 0 - Orchestration de la TODO
- [x] Cartographier les transitions reelles entre `GameState.PLAYING`, `GameState.PAUSED`, `GameState.OPTIONS` et le menu principal.
- [x] Choisir si le menu pause est un nouvel ecran dedie ou un overlay, en conservant la structure modulaire existante.
- [x] Definir la source de verite du chart courant pour permettre `restart` sans heuristique fragile.
- [x] Garder cette checklist synchronisee avec l'etat reel du depot pendant toute l'implementation.

## Agent 1 - Gameplay et UI
- [x] Ajouter un vrai menu pause ingame avec les entrees `reprendre`, `options`, `restart`, `quit`.
- [x] Brancher `ESC` en jeu sur l'ouverture et la fermeture controlee de la pause, sans retour direct au menu principal.
- [x] Geler le temps de jeu, le deplacement des notes, les animations dependantes du temps et l'audio a l'entree en pause.
- [x] Reprendre la partie via `reprendre` en conservant score, combo, precision, notes spawn, offsets et synchro audio.
- [x] Faire de `restart` un redemarrage propre du chart courant avec reset des groupes de sprites, des compteurs, des flags audio et du timer.
- [x] Faire de `quit` un retour propre au menu principal avec arret de l'audio et nettoyage de l'etat de partie.
- [x] Verifier le comportement en Free Play et en Story Mode, ou documenter clairement la limitation restante si une week multi-song n'est pas encore completement geree.

## Agent 2 - Recherche documentation et docs du depot
- [x] Verifier la documentation Pygame sur `pygame.mixer.music.pause()`, `unpause()`, `stop()` et les effets de reprise sur la synchro.
- [x] Verifier la bonne pratique de gestion d'inputs pour eviter les hits parasites pendant la pause et au retour des options.
- [x] Mettre a jour `README.md` avec la commande de pause et le comportement du menu ingame.
- [x] Mettre a jour `DOCS/USER_BIBLE.md` avec le parcours `pause -> reprendre/options/restart/quit`.
- [x] Mettre a jour `DOCS/DEVELOPER_BIBLE.md` avec la machine d'etats retenue, le flux de reprise et le flux de retour depuis les options ingame.
- [x] Mettre a jour `CHANGELOG.md` et `DOCS/KNOWLEDGE_LOG.md` avec les decisions, pieges et limites verifiees.

## Agent 3 - Code review et debug
- [x] Relire la machine d'etats pour eviter les regressions sur `SPACE`, `ESC`, sauvegarde des options et navigation des menus.
- [x] Verifier que `OptionsScreen` peut revenir au menu pause sans fuite d'etat ni retour parasite au menu principal.
- [x] Verifier que `restart` ne duplique pas la lecture audio, ne conserve pas de notes mortes et ne laisse pas d'objets orphelins.
- [x] Verifier que `quit` nettoie correctement l'audio, `current_week`, les drapeaux `playing/paused` et les groupes de sprites necessaires.
- [x] Traiter les warnings introduits par la feature comme des erreurs potentielles avant cloture.
- [x] Produire une passe de debug finale et documenter tout bug restant avant validation.

## Verification finale
- [x] Lancer `python main.py`.
- [x] Tester une partie Free Play: pause, reprendre, puis confirmer que le score et le timing continuent sur le meme chart.
- [x] Tester `options` depuis la pause, modifier au moins un volume ou keybind, revenir au menu pause puis reprendre.
- [x] Tester `restart` sur un chart avec audio disponible.
- [x] Tester `quit` depuis la pause et verifier le retour au menu principal sans audio residuel.
- [x] Tester un chart sans audio pour verifier le fallback en mode muet.
- [x] Confirmer que la documentation ne presente la feature comme disponible qu'une fois l'implementation et la validation bouclees.

## Resolution
- Implementation : `src/game.py` ajoute les transitions `PLAYING -> PAUSED -> PLAYING`, `PAUSED -> OPTIONS -> PAUSED`, `RESTART` et `QUIT`.
- UI : `src/menu.py` ajoute `PauseMenu` avec `RESUME`, `OPTIONS`, `RESTART`, `QUIT`.
- Documentation : `README.md`, `DOCS/USER_BIBLE.md`, `DOCS/DEVELOPER_BIBLE.md`, `CHANGELOG.md` et `DOCS/KNOWLEDGE_LOG.md` ont ete mis a jour.
- Verification : date de travail reverifiee localement avec `Get-Date` le `2026-04-12 03:58:29 +02:00`.
