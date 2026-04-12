# Backlog - Easter egg Konami Code Rickroll

Date de creation verifiee: 2026-04-12

## Regles de suivi
- [x] L'agent responsable de cette TODO maintient ce fichier a jour a chaque livraison partielle en cochant uniquement les taches effectivement en place.
- [x] Le backlog est deplace vers `TODOs/Implemented/` uniquement quand toutes les cases sont cochees et que les verifications finales sont passees.

## Criteres d'acceptation
- [x] L'easter egg est accessible depuis n'importe quel contexte ingame reellement actif : `GameState.PLAYING`, `GameState.PAUSED` et les options ouvertes depuis la pause.
- [x] L'activation repose sur la sequence canonique du Konami Code : `UP`, `UP`, `DOWN`, `DOWN`, `LEFT`, `RIGHT`, `LEFT`, `RIGHT`, `B`, `A`.
- [x] La detection du code n'interrompt pas les controles normaux du jeu et ne casse ni la pause ni les options ingame.
- [x] L'activation ouvre le navigateur par defaut sur `https://www.youtube.com/watch?v=dQw4w9WgXcQ&autoplay=1`.
- [x] Un message ingame affiche exactement `You've been so fuckin rick Rolled dude ! Ahah bad chance`.
- [x] L'activation ne doit pas ouvrir une pluie d'onglets si la sequence est repetee trop vite ou si une touche est maintenue.

## Agent 0 - Orchestration de la TODO
- [x] Cartographier les etats consideres comme ingame dans le code reel et definir un point unique de detection de la sequence.
- [x] Definir la politique de reset de la sequence : mauvaise touche, changement d'etat, perte de focus, retour menu principal.
- [x] Definir la politique d'anti-spam : cooldown, rearmement manuel ou limitation a une activation par session de chart.
- [x] Garder cette checklist synchronisee avec l'etat reel du depot pendant toute l'implementation.

## Agent 1 - Gameplay, input et UI
- [x] Ajouter un tracker de sequence global au runtime principal sans dupliquer la logique dans chaque ecran.
- [x] Limiter la detection du Konami Code aux contextes ingame, sans declenchement depuis la frontpage ou les menus hors partie.
- [x] Gerer correctement les `KEYDOWN` pertinents, les touches parasites et les remises a zero de sequence.
- [x] Ouvrir le navigateur par defaut de maniere non bloquante et avec gestion d'erreur explicite si l'ouverture echoue.
- [x] Afficher le message ingame exact `You've been so fuckin rick Rolled dude ! Ahah bad chance` via un overlay ou un composant UI temporaire visible en jeu.
- [x] Faire en sorte que le message reste lisible en gameplay actif, en pause et au retour des options ingame.
- [x] Verifier que l'easter egg n'introduit pas de regression sur les touches de gameplay, le menu pause et les retours d'options.

## Agent 2 - Recherche documentation et docs du depot
- [x] Verifier la methode Python recommandee pour ouvrir le navigateur par defaut sous Windows sans bloquer la boucle Pygame.
- [x] Verifier le comportement reel de l'URL YouTube avec `autoplay=1` et documenter clairement qu'un navigateur peut encore bloquer l'autoplay selon sa politique locale.
- [x] Verifier la bonne pratique Pygame pour suivre une sequence de touches globale sans consommer des evenements utiles aux autres ecrans.
- [x] Mettre a jour `README.md` avec l'existence de l'easter egg, sa sequence d'activation et la limite eventuelle de l'autoplay navigateur.
- [x] Mettre a jour `DOCS/USER_BIBLE.md` avec le comportement visible du message et l'ouverture externe.
- [x] Mettre a jour `DOCS/DEVELOPER_BIBLE.md` avec l'architecture retenue pour le tracker de sequence et le point d'integration dans la machine d'etats.
- [x] Mettre a jour `CHANGELOG.md` et `DOCS/KNOWLEDGE_LOG.md` avec les decisions, limites et pieges verifies.

## Agent 3 - Code review et debug
- [x] Relire la logique du buffer de touches pour eviter les faux positifs, les doubles activations et les regressions liees au key repeat.
- [x] Verifier la robustesse en cas de fenetre non focus, d'ouverture navigateur refusee ou de retour immediat au jeu.
- [x] Verifier que le message ingame ne laisse pas d'objets UI orphelins et ne perturbe pas le rendu du score ou de la pause.
- [x] Verifier qu'aucun warning nouveau n'est introduit ; traiter les warnings comme des erreurs potentielles avant cloture.
- [x] Produire une passe finale de debug et documenter les limites restantes, notamment autour de l'autoplay navigateur si elles ne sont pas maitrisables cote jeu.

## Verification finale
- [x] Lancer `python main.py`.
- [x] Tester le Konami Code pendant une partie active en Free Play.
- [x] Tester le Konami Code pendant le menu pause.
- [x] Tester le Konami Code depuis les options ouvertes en contexte ingame.
- [x] Verifier que le navigateur par defaut s'ouvre sur le bon lien YouTube.
- [x] Verifier que le message `You've been so fuckin rick Rolled dude ! Ahah bad chance` apparait bien ingame.
- [x] Verifier qu'une repetition rapide du code n'ouvre pas une rafale d'onglets.
- [x] Verifier que la frontpage et les menus hors partie ne declenchent pas l'easter egg si le scope final reste strictement ingame.
- [x] Documenter explicitement tout comportement d'autoplay que le navigateur pourrait bloquer malgre `autoplay=1`.

## Resolution
- Implementation : `src/game.py` ajoute le tracker `observe_konami_key()`, le scope `is_ingame_context()`, le cooldown anti-spam et l'overlay temporaire.
- Verification navigateur : l'appel a `webbrowser.open()` a ete verifie par remplacement controle de l'ouvreur pour eviter d'ouvrir un onglet reel pendant les tests automatises.
- Documentation : `README.md`, `DOCS/USER_BIBLE.md`, `DOCS/DEVELOPER_BIBLE.md`, `CHANGELOG.md` et `DOCS/KNOWLEDGE_LOG.md` ont ete mis a jour.
- Limite : `autoplay=1` est envoye dans l'URL, mais la politique du navigateur peut bloquer l'autoplay audible.
- Verification : date de travail reverifiee localement avec `Get-Date` le `2026-04-12 03:58:29 +02:00`.
