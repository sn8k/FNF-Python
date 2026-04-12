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
