"""
Exceptions métier personnalisées pour le tunnel de paiement.
"""


class ValidationError(Exception):
    """Exception levée en cas d'erreur de validation des données."""
    pass


class PaymentError(Exception):
    """Exception levée en cas d'erreur de traitement du paiement."""
    pass


class ConfirmationError(Exception):
    """Exception levée en cas d'erreur d'envoi de la confirmation."""
    pass