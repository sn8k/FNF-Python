quand on lance un chart ingame, le mp3 n'est pas chargé. Symptome : le chart ne se lance pas, l'audio est muté.

Resolution 2026-04-12 :
- verification headless : `Game.play_song('2hot BF mix')` avec `SDL_VIDEODRIVER=dummy` et `SDL_AUDIODRIVER=dummy`
- resultat : `audio_loaded=True` et fichier charge depuis `assets/Songs/2hot BF mix.mp3`
- comportement de repli observe dans le code : le chart continue en mode muet si l'audio est indisponible
