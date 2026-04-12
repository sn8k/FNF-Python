# Bible utilisateur

## Politique de logs
- le projet ecrit des logs utilisateur dans `logs/user.log`
- a chaque demarrage, les logs actifs sont recrees et les anciens sont archives en gardant 3 copies maximum
- les archives suivent le format `user.0.log` a `user.2.log` et `debug.0.log` a `debug.2.log`
- ces logs servent a donner des messages lisibles a l'utilisateur sans details techniques superflus
- l'affichage console des logs utilisateur se configure dans `data/config.json`, section `logging.user.console`
- `data/config.json` est recree automatiquement si le fichier manque ou devient invalide
- `data/settings.json` est recree ou complete automatiquement avec les cles manquantes au lancement

## Reglages disponibles
- `keybinds.<lane>.key` : nom logique de la touche memorisee pour compatibilite legacy
- `keybinds.<lane>.scancode` : touche physique prioritaire pour garder le meme placement entre qwerty et azerty
- `keybinds.<lane>.display` : libelle visible dans l'ecran d'options
- `logging.directory` : dossier de sortie des logs
- `logging.user.enabled` : active ou desactive le flux utilisateur
- `logging.user.level` : niveau minimal du flux utilisateur
- `logging.user.file` : nom du fichier de log utilisateur
- `logging.user.console` : affiche ou non les logs utilisateur dans la console
- `logging.debug.enabled` : active ou desactive le flux debug
- `logging.debug.level` : niveau minimal du flux debug
- `logging.debug.file` : nom du fichier de log debug
- `logging.debug.console` : affiche ou non les logs debug dans la console
- `gameplay.note_approach_time_ms` : temps de trajet des notes vers la zone de frappe, en millisecondes
- `display.mode` : mode d'affichage persistant, `windowed` ou `fullscreen`
- `menu.intro_enabled` : active ou desactive l'ecran d'intro au lancement
- `menu.intro_duration_ms` : duree d'affichage automatique de l'intro avant retour au menu principal
- `menu.exit_evasion_radius_px` : distance de souris qui declenche la fuite du bouton `QUIT` apres le code `AVRIL`
- `menu.exit_evasion_max_speed_px` : vitesse maximale ajoutee au bouton `QUIT` selon la vitesse de souris
- `menu.exit_evasion_smoothness` : lissage du deplacement du bouton `QUIT` evasif

## Usage recommande
- laisser `user.console` a `true` pour recevoir les messages importants
- laisser `debug.console` a `false` pour eviter de surcharger la console
- consulter `logs/debug.log` en cas de probleme de chargement d'asset, de JSON ou de configuration
- consulter `logs/debug.0.log` si le probleme a eu lieu au demarrage precedent
- les fichiers de `logs/` sont generes localement et ne doivent etre partages que pour diagnostiquer un probleme
- si vous supprimez `data/config.json` ou `data/settings.json`, le jeu les recreera au prochain lancement

## Keybinds et layouts
- par defaut, le gameplay garde les memes touches physiques sur qwerty et azerty : `A/S/W/D` sur qwerty devient `Q/S/Z/D` sur azerty
- l'ecran d'options memorise maintenant la touche physique et son libelle visible ; les anciens binds texte sont migres automatiquement au lancement
- si vous affectez une touche deja utilisee a une autre lane, l'ecran d'options echange les binds pour eviter les doublons instables

## Intro et frontpage
- au lancement, un ecran d'intro skippable affiche un grand lama velu avant le menu principal
- le titre de la frontpage bouge legerement pour attirer l'oeil sans perturber la navigation
- n'importe quelle touche ou un clic permet de passer l'intro sans attendre la fin du timer
- sur le menu principal, taper `AVRIL` active un easter egg ou le bouton `QUIT` fuit la souris sans sortir de la fenetre
- le 1er avril, l'easter egg `AVRIL` est active automatiquement au demarrage du menu principal

## Options d'affichage
- `WINDOWED` garde le jeu dans une fenetre 1280x720
- `FULLSCREEN` applique le meme canevas logique en plein ecran
- le changement est persistant et s'applique quand vous quittez l'ecran des options

## Lancement des outils
- menu Windows : `menu.bat`
- jeu principal : `python main.py`
- editeur de charts : `python -m src.chart_editor`
- gestionnaire de weeks et charts : `python -m src.week_manager`
- editeur de weeks : `python -m src.week_editor`
- `menu.bat` propose aussi une option pour lire les dernieres lignes de `logs/user.log` et `logs/debug.log`

## Free Play et difficultes
- le menu Free Play regroupe les fichiers par chanson
- si plusieurs difficultes existent, un menu de difficulte apparait avant de lancer le chart
- suffixes reconnus : `-easy` pour easy, `-hard` pour hard
- un fichier sans suffixe comme `spookeez.json` est considere comme la difficulte normale
- l'indication de controles en partie utilise les keybinds actuellement sauvegardes
- l'ecran d'options affiche le numero de version du projet en haut a droite

## Builds redistribuables
- build release : `scripts\build_release.bat -Clean`
- build debug : `scripts\build_debug.bat -Clean`
- build complet : `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build.ps1 -Configuration all -Clean`
- sortie release : `dist/FNF-Python-release/FNF-Python.exe` et `artifacts/FNF-Python-release.zip`
- sortie debug : `dist/FNF-Python-debug/FNF-Python-Debug.exe` et `artifacts/FNF-Python-debug.zip`
- les dossiers `assets/`, `data/` et `DOCS/` restent visibles dans le dossier redistribuable pour garder la customisation simple
- option `-SkipInstall` : ne pas installer les dependances avant le build
- option `-NoArchive` : generer uniquement le dossier dans `dist/`, sans zip dans `artifacts/`

## Audio des charts
- le jeu cherche un fichier audio dans `assets/Songs/` avec le nom du fichier de chart ou le champ `name` du chart
- les extensions testees sont `.mp3`, `.ogg`, puis `.wav`
- un chart peut definir un champ optionnel `audio` avec un chemin relatif, par exemple `assets/Songs/2hot BF mix.mp3`
- si l'audio est absent ou illisible, le chart reste jouable en mode muet et un avertissement est ecrit dans les logs

## Pause ingame
- en partie, `ESC` ouvre le menu pause au lieu de quitter directement le chart
- `RESUME` reprend la partie courante sans remettre a zero le score, le combo, le timer ou les notes deja apparues
- `OPTIONS` ouvre les options existantes, puis le bouton retour ramene au menu pause
- `RESTART` relance le chart courant depuis zero avec un etat de gameplay propre
- `QUIT` arrete l'audio et revient au menu principal
- pendant la pause, le timer du chart, les notes, les animations de score et l'audio restent figes

## Easter egg Konami Code
- contextes actifs : partie en cours, menu pause, options ouvertes depuis le menu pause
- sequence : `UP`, `UP`, `DOWN`, `DOWN`, `LEFT`, `RIGHT`, `LEFT`, `RIGHT`, `B`, `A`
- effet : ouverture du navigateur par defaut sur `https://www.youtube.com/watch?v=dQw4w9WgXcQ&autoplay=1`
- message visible : `You've been so fuckin rick Rolled dude ! Ahah bad chance`
- anti-spam : une activation est limitee par cooldown pour eviter une rafale d'onglets
- la sequence repart de zero si la fenetre perd le focus ou si vous quittez le contexte ingame
- limite : le navigateur peut bloquer l'autoplay malgre `autoplay=1`, selon sa politique locale

## Editeur de charts
- clic gauche : ajouter une note dans la lane cliquee
- clic droit : supprimer une note proche
- fleches gauche/droite : faire defiler la timeline
- fleches haut/bas : zoomer ou dezoomer
- `TAB` et `SHIFT+TAB` : changer de fichier audio de preview
- `P` : choisir le prochain dossier de personnage joueur
- `O` : choisir le prochain dossier de personnage ennemi
- `SPACE` : lancer ou mettre en pause la preview audio
- `CTRL+S` : sauvegarder le chart
- la sauvegarde exporte aussi `audio`, `player` et `enemy` quand ils sont selectionnes
- les informations de chart, preview et controles sont affichees dans le panneau bas de l'editeur
