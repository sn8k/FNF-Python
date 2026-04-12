Contexte :

Le projet vise a reproduire le fonctionnement du jeu Friday Night Funkin.
Il est mis en avant la partie customisation du projet par l'utilisateur.


Obligatoire :
- conserver un changelog verifie et verifiable.
- toute date utilisee doit etre verifiee avant apposition (exemple : si on code un jeudi 12 mars, on ne mettra pas 13 fevrier dans les logs, on verifie l'exactitude de la date avant utilisation)
- le projet doit avoir des logs user + debug, configurables via le fichier de configuration (reference a remplir)
- le projet doit etre versionne a chaque modification du code
- une bible utilisateur et developpeur doit etre produite et mise a jour tout le long du projet et de son developpement dans le dossier "DOCS".
- conserver une trace de toute nouvelle connaissance acquises et tout potentiel piege corrige et corrigeable, le but etant de ne jamais tomber 2 fois dans un meme piege.
- On s'adresse a l'utilisateur par le patronime de "Grand maitre chevelu", on cite une louange a la gloire du grand lama cosmique velu, celui qui peint les etoiles de par ses pets foireux magiques (humour).


Analyse verifiee du depot :
- point d'entree principal : `main.py`
- moteur principal : `src/game.py`
- menus et options : `src/menu.py`
- persistance des preferences utilisateur : `src/settings.py`
- sprites et objets de jeu : `src/sprites.py`
- editeur de charts : `src/chart_editor.py`
- gestion des weeks : `src/week_manager.py`
- editeur de weeks : `src/week_editor.py`
- configuration runtime : `data/config.json`
- preferences utilisateur : `data/settings.json`
- charts : `data/charts/*.json`
- weeks : `data/weeks/*.json`
- assets audio : `assets/Songs/`
- assets graphiques : `assets/sprites/`


Architecture actuelle a respecter :
- le projet repose sur `pygame` avec une structure simple et modulaire.
- les contenus personnalisables sont stockes dans des fichiers JSON et dans des dossiers d'assets, pas en dur dans le code.
- les modules sont separes par responsabilite ; toute nouvelle fonctionnalite doit suivre cette separation plutot que grossir un fichier unique.
- les chemins sont relatifs a la racine du projet ; ne pas introduire de chemins absolus.
- la customisation utilisateur doit rester une priorite : une option visible ou editable par l'utilisateur doit etre maintenue dans un format simple a modifier.
- la version finale devra etre redistribuable au format exe windows.

Sources de verite et priorites :
- le code reel et les fichiers JSON priment sur une supposition.
- le `README.md`, `DOCS/`, le changelog et les fichiers de configuration doivent etre alignes avec le comportement reel du code.
- si le code et la documentation divergent, il faut corriger soit le code soit la documentation, mais ne jamais laisser l'ecart sans trace.
- toute nouvelle option configurable doit etre documentee avec son emplacement, sa valeur par defaut et son effet.


Regles de modification du code :
- toute modification de gameplay, de menu, de configuration ou d'editeur doit verifier l'impact sur `README.md`, `DOCS/`, le changelog et les traces de connaissance.
- toute modification de schema JSON doit rester retrocompatible ou fournir une migration/documentation claire.
- toute nouvelle donnee persistante doit etre enregistree dans `data/` avec une structure lisible et stable.
- toute nouvelle fonctionnalite visible par l'utilisateur doit etre configurable si cela a du sens pour la customisation du projet.
- les logs techniques existants faits avec `print()` doivent tendre vers un vrai systeme de logs user/debug configurable ; ne pas multiplier les `print()` sauvages sans plan de migration.
- toute action en cas d'erreur doit etre explicite, avec comportement de repli documente si possible.
- On preferera toujours des fichiers de petites tailles avec une maintenance simplifiée, plutot que des monolythe impossibles a debugger.

Regles specifiques aux assets et donnees :
- un personnage jouable ou ennemi doit rester compatible avec l'arborescence `assets/sprites/Characters/...`.
- les charts doivent conserver le format minimal observe : `name`, `bpm`, `offset`, `notes`, avec des notes contenant au minimum `time` et `lane`.
- les weeks doivent conserver le format observe : `name`, `songs`, `enemies`, `background`.
- toute ressource manquante doit idealement avoir un fallback clair plutot qu'un crash brutal, comme c'est deja partiellement le cas pour certaines images.
- toute nouvelle ressource doit etre referencee de maniere coherente dans le code et la documentation.


Verification minimale apres changement :
- lancement principal : `python main.py`
- editeur de charts : `python -m src.chart_editor`
- editeur de weeks : `python -m src.week_editor`
- verification des fichiers JSON impactes apres ecriture
- verification du comportement de retour arriere si un asset ou un fichier manque


Pieges deja identifies apres lecture du code et du README :
- le `README.md` annonce certains comportements qui doivent etre reverifies avant toute reprise telle quelle.
- le gameplay principal affiche un chronometre et des notes, mais la lecture audio en partie n'est pas branchee comme dans l'editeur de charts ; ne pas documenter une fonctionnalite audio de jeu complet sans verification.
- `data/settings.json` contient actuellement des fleches directionnelles alors que le code de `src/game.py` mappe seulement `a`, `s`, `w`, `d` dans `apply_keybinds()` ; toute modification des controles doit traiter cette incoherence.
- le `README.md` et l'UI de `src/week_editor.py` ne sont pas parfaitement alignes sur la commande de sauvegarde ; le code sauvegarde avec `S`, alors que l'ecran affiche `CTRL+S`.
- plusieurs chaines de texte visibles montrent des problemes d'encodage ; eviter d'aggraver cet etat et verifier l'encodage des fichiers touches.
- l'etat du versionnage Git n'a pas pu etre verifie que via la commande locale si `git` est indisponible dans l'environnement ; ne jamais inventer une revision ou un commit.


Documentation et memoire projet :
- maintenir dans `DOCS/` une bible utilisateur et une bible developpeur.
- maintenir un journal des pieges, incoherences corrigees, decisions d'architecture et conventions de donnees.
- chaque correction importante doit laisser une trace comprensible : probleme, cause, solution, impact.
- si une verification n'a pas pu etre faite, l'indiquer explicitement dans la trace de travail ou la documentation mise a jour.


Communication attendue :
- toujours s'adresser a l'utilisateur comme "Grand maitre chevelu".
- conserver un ton respectueux, clair, utile, avec une touche d'humour compatible avec la louange au grand lama cosmique velu, Lama parmis les lamas, dieux des poils longs et prophete de la sainte odeur de bouc sacrée.
- ne pas presenter une hypothese comme un fait verifie.
