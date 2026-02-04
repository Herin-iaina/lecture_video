"""
Client HTTP pour communiquer avec l'API Video Analytics.

Ce module remplace l'acces direct a la base de donnees.
"""

import logging
from typing import Optional
from urllib.parse import urljoin

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None

logger = logging.getLogger(__name__)


class APIClient:
    """Client pour l'API Video Analytics."""

    def __init__(self, base_url: str, machine_name: str, timeout: float = 5.0):
        """
        Initialise le client API.

        Args:
            base_url: URL de base de l'API (ex: http://server:8000)
            machine_name: Nom de cette borne
            timeout: Timeout des requetes en secondes
        """
        self.base_url = base_url.rstrip("/")
        self.machine_name = machine_name
        self.timeout = timeout
        self._enabled = REQUESTS_AVAILABLE

        if not self._enabled:
            logger.warning("requests non disponible - logging API desactive")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None
    ) -> Optional[dict]:
        """
        Effectue une requete HTTP.

        Args:
            method: Methode HTTP (GET, POST, etc.)
            endpoint: Endpoint relatif (ex: /choices)
            json: Corps de la requete en JSON
            params: Parametres de requete

        Returns:
            Reponse JSON ou None en cas d'erreur.
        """
        if not self._enabled:
            return None

        url = urljoin(self.base_url, endpoint)

        try:
            response = requests.request(
                method=method,
                url=url,
                json=json,
                params=params,
                timeout=self.timeout
            )

            if response.status_code >= 400:
                logger.error(f"Erreur API {response.status_code}: {response.text}")
                return None

            if response.status_code == 204:
                return {}

            return response.json()

        except requests.exceptions.ConnectionError:
            logger.warning(f"Serveur API non accessible: {self.base_url}")
            return None
        except requests.exceptions.Timeout:
            logger.warning("Timeout de la requete API")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur requete API: {e}")
            return None

    def health_check(self) -> bool:
        """
        Verifie si le serveur API est accessible.

        Returns:
            True si le serveur repond, False sinon.
        """
        result = self._make_request("GET", "/health")
        return result is not None and result.get("status") == "ok"

    def log_choice(self, choice: str, video_path: str) -> bool:
        """
        Enregistre un choix utilisateur sur le serveur.

        Args:
            choice: Lettre du bouton presse (A-G)
            video_path: Chemin de la video jouee

        Returns:
            True si l'enregistrement a reussi, False sinon.
        """
        payload = {
            "choix": choice.upper(),
            "video": video_path,
            "machine": self.machine_name
        }

        result = self._make_request("POST", "/choices", json=payload)

        if result:
            logger.debug(f"Choix enregistre: {choice} -> {video_path}")
            return True
        return False

    def register_machine(
        self,
        description: Optional[str] = None,
        location: Optional[str] = None
    ) -> bool:
        """
        Enregistre cette machine sur le serveur.

        Args:
            description: Description de la borne
            location: Emplacement de la borne

        Returns:
            True si l'enregistrement a reussi, False sinon.
        """
        payload = {
            "name": self.machine_name,
            "description": description,
            "location": location
        }

        result = self._make_request("POST", "/machines", json=payload)

        # 409 = deja enregistree, ce n'est pas une erreur
        if result is not None:
            logger.info(f"Machine enregistree: {self.machine_name}")
            return True
        return False

    def get_stats(self, days: int = 7) -> Optional[dict]:
        """
        Recupere les statistiques depuis le serveur.

        Args:
            days: Nombre de jours a analyser

        Returns:
            Dictionnaire des statistiques ou None.
        """
        params = {
            "machine": self.machine_name,
            "days": days
        }
        return self._make_request("GET", "/stats", params=params)

    @property
    def is_enabled(self) -> bool:
        """Indique si le client API est actif."""
        return self._enabled
