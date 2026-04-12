# Bible developpeur

## Politique de logs
- utiliser `src.logging_utils.configure_logging()` au bootstrap des scripts executables
- utiliser `get_user_logger(...)` pour les messages orientes utilisateur
- utiliser `get_debug_logger(...)` pour les details techniques, exceptions et diagnostics
- eviter les `print()` directs dans le code applicatif ; si un cas exceptionnel reste necessaire, il doit etre justifie

## Convention d'usage
- un message court et comprehensible pour l'utilisateur dans le logger `user`
- le detail technique, le chemin de fichier ou l'exception dans le logger `debug`
- les nouvelles options de logs doivent etre ajoutees dans `data/config.json` et documentees dans cette bible et la bible utilisateur

## Points de vigilance connus
- `main.py` configure les logs avant l'initialisation principale
- `Game` recharge la configuration via `load_project_config()` pour garantir la presence du bloc `logging`
- les modules d'edition peuvent etre lances seuls ; ils configurent donc aussi les logs au bootstrap
- `src.chart_editor`, `src.week_editor` et `src.week_manager` doivent rester lancables via `python -m ...`
- les outils d'edition ajoutent la racine du projet au `sys.path` uniquement quand ils sont executes comme fichiers directs, pour garder les imports `src.*` compatibles
- `Game.play_song()` recharge les sprites et l'etat de notes a chaque chart pour eviter les restes d'une partie precedente
- les temps de notes des charts sont des temps de frappe cibles ; `Note.update()` positionne la note pour arriver sur la zone de frappe a ce temps
- le champ optionnel `audio` d'un chart doit rester relatif a la racine du projet ; les chemins absolus sont ignores et journalises
- si aucun audio n'est trouve dans `assets/Songs/`, le gameplay doit continuer en mode muet avec un avertissement utilisateur et un detail debug

## Configuration gameplay
- `gameplay.spawn_distance` : distance visuelle entre le point d'apparition et la zone de frappe
- `gameplay.note_approach_time_ms` : duree du trajet de la note vers la zone de frappe
- `note_size` reste au niveau racine de `data/config.json` ; le spawn de notes construit une configuration combinee pour `Note`

## Pause ingame
- `GameState.PAUSED` est un etat dedie : `update()` ne fait pas avancer le timer, ne spawne pas de notes et ne met pas a jour les sprites de gameplay
- `ESC` depuis `GameState.PLAYING` appelle `show_pause_menu()` ; `ESC` dans `PauseMenu` appelle `resume_from_pause()`
- `PauseMenu` vit dans `src.menu` et reutilise `Button` pour `RESUME`, `OPTIONS`, `RESTART`, `QUIT`
- `show_pause_options()` instancie `OptionsScreen` avec `back_to_pause_menu()` pour eviter un retour parasite au menu principal
- `restart_current_song()` s'appuie sur `current_song_key`, defini dans `play_song()`, pour relancer le chart courant sans heuristique sur le nom affiche
- `quit_to_main_menu()` arrete l'audio, remet l'etat de partie a zero, nettoie `current_week` et `current_song_key`, puis revient a `GameState.MENU`
- la reprise audio s'appuie sur `pygame.mixer.music.pause()` et `unpause()` ; la doc Pygame indique que `get_pos()` mesure le temps de lecture et ne tient pas compte des offsets de depart
- la boucle continue d'appeler `pygame.event.get()` a chaque frame, y compris en pause/options, pour eviter de saturer la queue d'evenements Pygame

## Easter egg Konami Code
- la detection est centralisee dans `Game.handle_events()` via `observe_konami_key()` et ne consomme pas les evenements, pour laisser les ecrans existants traiter les controles normaux
- `is_ingame_context()` limite le scope a `PLAYING`, `PAUSED` et `OPTIONS` seulement quand `options_opened_from_pause` est vrai
- le buffer est remis a zero sur mauvaise touche, retour menu principal, ouverture des options principales ou `QUIT`
- `activate_konami_easter_egg()` applique `KONAMI_COOLDOWN_MS` pour eviter plusieurs ouvertures rapides
- l'ouverture externe utilise `webbrowser.open(..., new=2, autoraise=True)` dans un thread daemon ; toute exception ou retour `False` est journalise
- `draw_konami_message()` affiche le message temporaire au-dessus du gameplay, de la pause ou des options ingame, sans creer de sprite persistant
- l'URL contient `autoplay=1`, mais le navigateur garde la decision finale sur l'autoplay audible

## Packaging PyInstaller
- les specs sont dans `packaging/pyinstaller/fnf_release.spec` et `packaging/pyinstaller/fnf_debug.spec`
- le script central est `scripts/build.ps1`; les wrappers Windows sont `scripts/build_release.bat` et `scripts/build_debug.bat`
- les builds sont en mode one-folder, pas one-file, pour garder `assets/`, `data/` et `DOCS/` modifiables par l'utilisateur final
- `contents_directory="."` doit rester sur l'appel `EXE(...)` des specs PyInstaller, ce qui impose `pyinstaller>=6.0` dans `requirements-dev.txt`
- les specs excluent les paquets optionnels non utilises (`numpy`, `PIL`, `pytest`, `setuptools`, etc.) pour limiter les warnings et la taille du build
- le script de build retente la compression zip si Windows garde temporairement un fichier PyInstaller verrouille
- les artefacts generes `build/`, `dist/` et `artifacts/` sont ignores par Git
- toute nouvelle donnee necessaire au runtime doit etre ajoutee aux `datas` des deux specs

## Hygiene Git
- le `.gitignore` exclut les caches Python, environnements virtuels, logs generes, secrets locaux, caches d'outils et sorties de build
- un fichier deja suivi par Git n'est pas retire du depot par le seul ajout d'une regle `.gitignore`
- pour retirer une pollution deja suivie sans supprimer le fichier local, utiliser `git rm --cached` sur le chemin concerne puis committer la suppression d'index
- ne pas ignorer `assets/`, `data/charts/` ou `data/weeks/` globalement : ce sont des sources de verite customisables du projet
