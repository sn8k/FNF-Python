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

## Usage recommande
- laisser `user.console` a `true` pour recevoir les messages importants
- laisser `debug.console` a `false` pour eviter de surcharger la console
- consulter `logs/debug.log` en cas de probleme de chargement d'asset, de JSON ou de configuration
