Feature request : 
Easter Egg activable en tapant "AVRIL" sur son clavier :
   - Le bouton sortie du menu principal fuit pour ne pas se faire clicker par la souris
   - le bouton ne DOIT pas sortir de la fenetre
   - il doit etre en fonction de la vitesse de la souris, pas predictable du mouvement de la souris.
   - la vitesse du bouton doit etre modulée par la vitesse de deplacement de la souris
   - le movement se fait de maniere smooth, comme le titre de la front page.

Implementation 2026-04-12 :
- `MenuScreen` detecte la sequence `AVRIL` sur le menu principal.
- Le bouton `QUIT` fuit la souris avec une vitesse modulee par la vitesse de deplacement de la souris.
- La position est limitee a la fenetre 1280x720.
- Les reglages sont configurables dans `data/config.json`, section `menu`.
