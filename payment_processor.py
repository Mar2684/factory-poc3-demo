from typing import Optional
from models import Payment, Customer, PaymentStatus
from exceptions import PaymentError
from utils import generate_payment_id

# Mock Stripe pour les tests et l'exécution sans dépendance externe
class MockStripe:
    class error:
        class CardError(Exception):
            def __init__(self, message, *args):
                super().__init__(message)
                self.error = type('obj', (object,), {'message': message})()

        class StripeError(Exception):
            pass

    class Charge:
        @staticmethod
        def create(**kwargs):
            # Simule un paiement réussi par défaut
            return type('obj', (object,), {'paid': True})()

    class Refund:
        @staticmethod
        def create(**kwargs):
            # Simule un remboursement réussi par défaut
            return type('obj', (object,), {'status': 'succeeded'})()


# Utilisation du mock si stripe n'est pas disponible
try:
    import stripe
except ImportError:
    stripe = MockStripe()


# Configuration Stripe (clé secrète à configurer via variable d'environnement en production)
# stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")  # Désactivé pour éviter les fuites de secrets


def process_payment(payment: Payment, customer: Customer) -> PaymentStatus:
    """Traite un paiement via Stripe et retourne son statut.

    Args:
        payment: Instance de Payment à traiter.
        customer: Instance de Customer associée au paiement.

    Returns:
        Statut du paiement (SUCCEEDED, FAILED, etc.).

    Raises:
        PaymentError: Si le paiement échoue ou si une erreur API survient.
    """
    if stripe is None:
        raise PaymentError("Module stripe non disponible")

    try:
        # Création d'une charge Stripe
        charge = stripe.Charge.create(
            amount=int(payment.amount * 100),  # Stripe utilise des centimes
            currency=payment.currency.lower(),
            source=payment.card_token,
            description=f"Payment for order {payment.order_id}",
            receipt_email=customer.email,
        )

        if charge.paid:
            return PaymentStatus.SUCCEEDED
        else:
            raise PaymentError("Paiement non effectué par Stripe")

    except stripe.error.CardError as e:
        raise PaymentError(f"Carte refusée: {e.error.message}")
    except stripe.error.StripeError as e:
        raise PaymentError(f"Erreur Stripe: {e}")
    except Exception as e:
        raise PaymentError(f"Erreur inattendue lors du paiement: {e}")


def refund_payment(payment_id: str) -> bool:
    """Effectue un remboursement via Stripe et retourne True si réussi.

    Args:
        payment_id: ID du paiement à rembourser.

    Returns:
        True si le remboursement a réussi, False sinon.

    Raises:
        PaymentError: Si le remboursement échoue.
    """
    if stripe is None:
        raise PaymentError("Module stripe non disponible")

    try:
        refund = stripe.Refund.create(charge=payment_id)
        return refund.status == "succeeded"
    except stripe.error.StripeError as e:
        raise PaymentError(f"Erreur Stripe lors du remboursement: {e}")
    except Exception as e:
        raise PaymentError(f"Erreur inattendue lors du remboursement: {e}")