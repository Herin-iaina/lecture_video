#!/usr/bin/env python3
"""
Client video interactif pour bornes/kiosques.

Ce script gere la lecture de videos en reponse aux commandes
recues via port serie depuis un microcontroleur Arduino.
Les donnees sont envoyees au serveur API centralise.
"""

import logging
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

import serial
from serial import SerialException

from config import SerialConfig, VideoConfig, AppConfig, LogConfig, APIConfig
from api_client import APIClient

# Configuration du logging
logging.basicConfig(
    level=getattr(logging, LogConfig.LEVEL),
    format=LogConfig.FORMAT,
    datefmt=LogConfig.DATE_FORMAT,
)

if LogConfig.FILE:
    file_handler = logging.FileHandler(LogConfig.FILE)
    file_handler.setFormatter(logging.Formatter(LogConfig.FORMAT, LogConfig.DATE_FORMAT))
    logging.getLogger().addHandler(file_handler)

logger = logging.getLogger(__name__)


class VideoPlayer:
    """Gestionnaire de lecture video avec MPV."""

    def __init__(self):
        """Initialise le lecteur video."""
        self._process: Optional[subprocess.Popen] = None

    def stop(self) -> None:
        """Arrete la video en cours de lecture."""
        if self._process and self._process.poll() is None:
            logger.debug("Arret de la video en cours")
            self._process.terminate()
            time.sleep(AppConfig.STOP_DELAY)
            if self._process.poll() is None:
                self._process.kill()

    def play(self, video_path: Path, loop: bool = False) -> bool:
        """
        Lance la lecture d'une video.

        Args:
            video_path: Chemin vers le fichier video.
            loop: Si True, la video boucle indefiniment.

        Returns:
            True si la lecture a demarre, False sinon.
        """
        if not video_path.exists():
            logger.error(f"Video introuvable: {video_path}")
            return False

        self.stop()

        cmd = ["mpv", "--fs", "--no-terminal"]
        if loop:
            cmd.append("--loop")
        cmd.append(str(video_path))

        logger.info(f"Lecture: {video_path.name}")
        try:
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except FileNotFoundError:
            logger.error("MPV non installe ou non trouve dans le PATH")
            return False
        except OSError as e:
            logger.error(f"Erreur lancement MPV: {e}")
            return False

    def play_generic(self) -> bool:
        """Lance la video generique en boucle."""
        generic_path = VideoConfig.generic_path()
        if not generic_path.exists():
            logger.error(f"Video generique introuvable: {generic_path}")
            return False
        return self.play(generic_path, loop=True)

    def wait_for_end(self, timeout: Optional[float] = None) -> bool:
        """
        Attend la fin de la video en cours.

        Args:
            timeout: Delai maximum en secondes (None = infini).

        Returns:
            True si la video s'est terminee normalement, False si timeout.
        """
        if not self._process:
            return True

        try:
            self._process.wait(timeout=timeout)
            return True
        except subprocess.TimeoutExpired:
            logger.warning("Timeout - arret force de la video")
            self.stop()
            return False

    @property
    def is_playing(self) -> bool:
        """Indique si une video est en cours de lecture."""
        return self._process is not None and self._process.poll() is None


class SerialController:
    """Gestionnaire de communication serie avec l'Arduino."""

    def __init__(self):
        """Initialise le controleur serie."""
        self._serial: Optional[serial.Serial] = None

    def connect(self) -> bool:
        """
        Etablit la connexion au port serie.

        Returns:
            True si la connexion est etablie, False sinon.
        """
        try:
            self._serial = serial.Serial(
                port=SerialConfig.PORT,
                baudrate=SerialConfig.BAUDRATE,
                timeout=SerialConfig.TIMEOUT
            )
            logger.info(f"Port serie connecte: {SerialConfig.PORT}")
            return True
        except SerialException as e:
            logger.error(f"Erreur connexion port serie: {e}")
            return False

    def disconnect(self) -> None:
        """Ferme la connexion serie."""
        if self._serial and self._serial.is_open:
            self._serial.close()
            logger.info("Port serie ferme")

    def read_command(self) -> Optional[str]:
        """
        Lit une commande depuis le port serie.

        Returns:
            La commande lue (A-G) ou None si invalide/vide.
        """
        if not self._serial or not self._serial.is_open:
            return None

        try:
            data = self._serial.readline().decode("utf-8").strip().upper()

            if not data:
                return None

            if data not in VideoConfig.VALID_COMMANDS:
                if data != "READY":
                    logger.warning(f"Commande inconnue: {data}")
                return None

            logger.debug(f"Commande recue: {data}")
            return data

        except UnicodeDecodeError:
            logger.warning("Erreur decodage donnees serie")
            return None
        except SerialException as e:
            logger.error(f"Erreur lecture serie: {e}")
            return None

    @property
    def is_connected(self) -> bool:
        """Indique si le port serie est connecte."""
        return self._serial is not None and self._serial.is_open


def get_latest_video(folder: Path) -> Optional[Path]:
    """
    Trouve la video la plus recente dans un dossier.

    Args:
        folder: Chemin du dossier a analyser.

    Returns:
        Le chemin vers la video la plus recente, ou None si aucune.
    """
    videos = []
    for ext in VideoConfig.SUPPORTED_EXTENSIONS:
        videos.extend(folder.glob(f"*{ext}"))

    if not videos:
        return None

    return max(videos, key=lambda f: f.stat().st_mtime)


class Application:
    """Application principale du client video."""

    def __init__(self):
        """Initialise l'application."""
        self.player = VideoPlayer()
        self.serial = SerialController()
        self.api = APIClient(
            base_url=APIConfig.BASE_URL,
            machine_name=APIConfig.MACHINE_NAME,
            timeout=APIConfig.TIMEOUT
        )
        self.running = False
        self._last_cmd: Optional[str] = None
        self._last_event_time: float = 0

    def setup(self) -> bool:
        """
        Initialise les composants de l'application.

        Returns:
            True si l'initialisation a reussi, False sinon.
        """
        # Verification de la connexion API
        if self.api.health_check():
            logger.info(f"Connecte au serveur API: {APIConfig.BASE_URL}")
            # Enregistrement de la machine
            self.api.register_machine(
                description=APIConfig.MACHINE_DESCRIPTION,
                location=APIConfig.MACHINE_LOCATION
            )
        else:
            logger.warning("Serveur API non accessible - mode hors ligne")

        # Connexion au port serie
        if not self.serial.connect():
            return False

        # Demarrage de la video generique
        if not self.player.play_generic():
            logger.warning("Impossible de lancer la video generique")

        return True

    def cleanup(self) -> None:
        """Nettoie les ressources avant arret."""
        logger.info("Arret de l'application")
        self.player.stop()
        self.serial.disconnect()

    def handle_command(self, command: str) -> None:
        """
        Traite une commande recue.

        Args:
            command: La commande a traiter (A-G).
        """
        now = time.time()

        # Anti-spam
        if now - self._last_event_time < AppConfig.MIN_INTERVAL:
            logger.debug("Commande ignoree (anti-spam)")
            return

        # Evite double declenchement
        if command == self._last_cmd:
            return

        folder = VideoConfig.ROOT / command

        if not folder.is_dir():
            logger.error(f"Dossier manquant: {folder}")
            return

        latest_video = get_latest_video(folder)

        if not latest_video:
            logger.warning(f"Aucune video dans {folder}")
            return

        # Lecture de la video selectionnee
        if self.player.play(latest_video):
            # Log sur le serveur API
            self.api.log_choice(command, str(latest_video))

            # Attendre la fin de la video
            self.player.wait_for_end()

            # Retour a la video generique
            self.player.play_generic()

            self._last_cmd = command
            self._last_event_time = now

    def run(self) -> None:
        """Boucle principale de l'application."""
        self.running = True
        logger.info(f"Application demarree - Machine: {APIConfig.MACHINE_NAME}")

        while self.running:
            try:
                command = self.serial.read_command()
                if command:
                    self.handle_command(command)

            except KeyboardInterrupt:
                logger.info("Arret demande par l'utilisateur")
                self.running = False


def main() -> int:
    """
    Point d'entree principal.

    Returns:
        Code de sortie (0 = succes, 1 = erreur).
    """
    app = Application()

    # Gestion du signal SIGTERM pour arret propre
    def signal_handler(_signum, _frame):
        logger.info("Signal recu, arret en cours...")
        app.running = False

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        if not app.setup():
            logger.error("Echec de l'initialisation")
            return 1

        app.run()
        return 0

    except Exception as e:
        logger.exception(f"Erreur fatale: {e}")
        return 1

    finally:
        app.cleanup()


if __name__ == "__main__":
    sys.exit(main())
