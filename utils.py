import uuid
import logging
from typing import Dict


def generate_order_id() -> str:
    """Génère un UUID v4 pour une commande."""
    return str(uuid.uuid4())


def generate_payment_id() -> str:
    """Génère un UUID v4 pour un paiement."""
    return str(uuid.uuid4())


def format_currency(amount: float, currency: str = "EUR") -> str:
    """Formate un montant en devise.

    Args:
        amount: Montant à formater.
        currency: Code devise (par défaut EUR).

    Returns:
        Montant formaté sous forme de chaîne.
    """
    return f"{amount:.2f} {currency}"


def log_checkout_event(event: str, order_id: str, status: str) -> None:
    """Journalise un événement du checkout.

    Args:
        event: Type d'événement (ex: 'checkout_started').
        order_id: ID de la commande.
        status: Statut de l'événement.
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info(f"Event: {event}, Order ID: {order_id}, Status: {status}")