# Bible utilisateur

## Politique de logs
- le projet ecrit des logs utilisateur dans `logs/user.log`
- ces logs servent a donner des messages lisibles a l'utilisateur sans details techniques superflus
- l'affichage console des logs utilisateur se configure dans `data/config.json`, section `logging.user.console`

## Reglages disponibles
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

## Usage recommande
- laisser `user.console` a `true` pour recevoir les messages importants
- laisser `debug.console` a `false` pour eviter de surcharger la console
- consulter `logs/debug.log` en cas de probleme de chargement d'asset, de JSON ou de configuration
- les fichiers de `logs/` sont generes localement et ne doivent etre partages que pour diagnostiquer un probleme

## Lancement des outils
- jeu principal : `python main.py`
- editeur de charts : `python -m src.chart_editor`
- gestionnaire de weeks et charts : `python -m src.week_manager`
- editeur de weeks : `python -m src.week_editor`

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

## Editeur de charts
- clic gauche : ajouter une note dans la lane cliquee
- clic droit : supprimer une note proche
- fleches gauche/droite : faire defiler la timeline
- fleches haut/bas : zoomer ou dezoomer
- `TAB` et `SHIFT+TAB` : changer de fichier audio de preview
- `SPACE` : lancer ou mettre en pause la preview audio
- `CTRL+S` : sauvegarder le chart
