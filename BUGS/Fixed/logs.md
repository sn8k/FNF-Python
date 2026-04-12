les logs doivent etre reinitialisé a chaque demarrage. une copie des logs precedents doivent etre conservés a hauteur de 3 maximum, avec normalisation du nom en <logname>.0.log jusqu'a <logname>.2.log. 

Correction 2026-04-12 :
- `configure_logging()` archive les logs existants avant d'ouvrir les nouveaux fichiers actifs.
- Les archives sont conservees avec le format `<logname>.0.log`, `<logname>.1.log`, `<logname>.2.log`.
- Les handlers existants sont fermes avant rotation pour eviter les verrous Windows.
