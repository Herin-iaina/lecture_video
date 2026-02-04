"""
Configuration du client video (borne).

Charge les parametres depuis les variables d'environnement ou un fichier .env.
"""

import os
from pathlib import Path
from typing import List

# Charge le fichier .env s'il existe
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass


class SerialConfig:
    """Configuration du port serie."""
    PORT: str = os.getenv("SERIAL_PORT", "/dev/ttyUSB0")
    BAUDRATE: int = int(os.getenv("BAUDRATE", "9600"))
    TIMEOUT: float = 1.0


class VideoConfig:
    """Configuration des videos."""
    ROOT: Path = Path(os.getenv("VIDEO_ROOT", "./videos"))
    GENERIC_NAME: str = os.getenv("GENERIC_VIDEO_NAME", "generic.mp4")
    VALID_COMMANDS: List[str] = ["A", "B", "C", "D", "E", "F", "G"]
    SUPPORTED_EXTENSIONS: List[str] = [".mp4", ".mkv", ".avi", ".mov", ".webm"]

    @classmethod
    def generic_path(cls) -> Path:
        """Retourne le chemin complet vers la video generique."""
        return cls.ROOT / cls.GENERIC_NAME


class APIConfig:
    """Configuration de l'API serveur."""
    BASE_URL: str = os.getenv("API_URL", "http://localhost:8000")
    TIMEOUT: float = float(os.getenv("API_TIMEOUT", "5.0"))

    # Identifiant de cette borne
    MACHINE_NAME: str = os.getenv("MACHINE_NAME", "borne_01")
    MACHINE_DESCRIPTION: str = os.getenv("MACHINE_DESCRIPTION", "")
    MACHINE_LOCATION: str = os.getenv("MACHINE_LOCATION", "")


class LogConfig:
    """Configuration du logging."""
    LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    FILE: str = os.getenv("LOG_FILE", "")
    FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"


class AppConfig:
    """Configuration generale de l'application."""
    # Intervalle minimum entre deux choix (anti-spam)
    MIN_INTERVAL: float = float(os.getenv("MIN_INTERVAL", "5"))

    # Delai avant de terminer un processus video
    STOP_DELAY: float = 0.3
