"""
FNF Lightweight - Setup Checker
This script helps with installing required dependencies
"""
import subprocess
import sys

from src.logging_utils import configure_logging, get_debug_logger, get_user_logger


configure_logging()
user_logger = get_user_logger("setup_check")
debug_logger = get_debug_logger("setup_check")


def check_pygame():
    """Check if pygame is installed"""
    try:
        import pygame

        user_logger.info("Pygame %s est installe.", pygame.ver)
        return True
    except ImportError:
        user_logger.warning("Pygame n'est pas installe.")
        return False


def install_pygame():
    """Try to install pygame"""
    user_logger.info("Tentative d'installation de pygame.")

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame==2.5.0", "--upgrade"])
        user_logger.info("Pygame a ete installe avec succes.")
        return True
    except Exception as exc:
        user_logger.error("L'installation de pygame a echoue.")
        debug_logger.exception("Echec de l'installation de pygame: %s", exc)
        return False


def main():
    """Main setup checker"""
    user_logger.info("FNF Lightweight - Setup Checker")
    debug_logger.info("Version Python: %s", sys.version)
    debug_logger.info("Executable Python: %s", sys.executable)

    if check_pygame():
        user_logger.info("Toutes les dependances sont installees. Lancez: python main.py")
        return 0

    response = input("Would you like to install pygame now? (y/n): ").strip().lower()

    if response == "y":
        if install_pygame():
            user_logger.info("Setup termine. Lancez: python main.py")
            return 0

        user_logger.error("L'installation a echoue.")
        user_logger.info("Piste 1: pip install --user pygame")
        user_logger.info("Piste 2: conda install pygame")
        user_logger.info("Piste 3: utiliser Python officiel depuis python.org")
        return 1

    user_logger.info("Installation manuelle requise: pip install pygame==2.5.0")
    return 1


if __name__ == "__main__":
    sys.exit(main())
