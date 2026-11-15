from typing import Dict
from models import Order, Payment, CheckoutStatus
from validation import validate_order, validate_payment
from payment_processor import process_payment, refund_payment
from confirmation import generate_confirmation_email, send_confirmation_email
from exceptions import ValidationError, PaymentError, ConfirmationError
from utils import generate_order_id, generate_payment_id, log_checkout_event


class CheckoutService:
    """Service principal orchestrant le tunnel de paiement."""

    def execute_checkout(self, order_data: Dict, payment_data: Dict) -> CheckoutStatus:
        """Orchestration complète du checkout.

        Args:
            order_data: Données de la commande.
            payment_data: Données de paiement.

        Returns:
            Statut final du checkout.

        Raises:
            ValidationError: Si les données sont invalides.
            PaymentError: Si le paiement échoue.
            ConfirmationError: Si l'envoi de la confirmation échoue.
        """
        try:
            # Génération des IDs
            order_id = generate_order_id()
            payment_id = generate_payment_id()

            # Validation des données
            order = validate_order(order_data)
            order.id = order_id
            payment = validate_payment(payment_data)
            payment.id = payment_id
            payment.order_id = order_id

            # Journalisation
            log_checkout_event("checkout_started", order_id, CheckoutStatus.PENDING)

            # Traitement du paiement
            payment_status = process_payment(payment, order.customer)
            if payment_status != "SUCCEEDED":
                raise PaymentError("Paiement non abouti")

            log_checkout_event("payment_succeeded", order_id, CheckoutStatus.PAID)

            # Génération et envoi de la confirmation
            email_html, email_text = generate_confirmation_email(order)
            confirmation_status = send_confirmation_email(order, email_html, email_text)
            if confirmation_status != "SENT":
                raise ConfirmationError("Échec de l'envoi de la confirmation")

            log_checkout_event("confirmation_sent", order_id, CheckoutStatus.CONFIRMED)

            return CheckoutStatus.CONFIRMED

        except ValidationError as e:
            log_checkout_event("validation_failed", "", CheckoutStatus.FAILED)
            raise
        except PaymentError as e:
            log_checkout_event("payment_failed", "", CheckoutStatus.FAILED)
            # Tentative de remboursement si paiement déjà effectué
            if "payment_id" in locals():
                try:
                    refund_payment(payment_id)
                    log_checkout_event("refund_initiated", order_id, CheckoutStatus.FAILED)
                except Exception:
                    pass
            raise
        except ConfirmationError as e:
            log_checkout_event("confirmation_failed", order_id, CheckoutStatus.FAILED)
            raise
        except Exception as e:
            log_checkout_event("checkout_failed", "", CheckoutStatus.FAILED)
            raise


def execute_checkout(order_data: Dict, payment_data: Dict) -> CheckoutStatus:
    """Fonction d'entrée pour l'exécution du checkout.

    Args:
        order_data: Données de la commande.
        payment_data: Données de paiement.

    Returns:
        Statut final du checkout.
    """
    service = CheckoutService()
    return service.execute_checkout(order_data, payment_data)