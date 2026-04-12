"""
Friday Night Funkin' Lightweight - Main Entry Point
"""
import sys
from src.logging_utils import configure_logging, get_debug_logger, get_user_logger

PROJECT_CONFIG = configure_logging()
user_logger = get_user_logger("main")
debug_logger = get_debug_logger("main")

# Check if pygame is installed
try:
    import pygame
except ImportError:
    user_logger.error("Pygame n'est pas installe.")
    user_logger.info("Commande recommandee: pip install pygame==2.5.0")
    user_logger.info("Alternative utilisateur: pip install --user pygame==2.5.0")
    user_logger.info("Alternative conda: conda install pygame")
    user_logger.info("Script d'aide: python setup_check.py")
    user_logger.info("Si Python vient du Microsoft Store, preferer python.org ou Anaconda.")
    sys.exit(1)

from src.game import Game

def main():
    debug_logger.debug("Initialisation de pygame avec la configuration chargee.")
    pygame.init()
    
    game = Game()
    user_logger.info("Demarrage du jeu.")
    game.run()
    
    user_logger.info("Fermeture du jeu.")
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
