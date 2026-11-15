import unittest
from unittest.mock import patch, MagicMock
from payment_processor import process_payment, refund_payment
from exceptions import PaymentError
from models import Payment, Customer, PaymentStatus


class TestPaymentProcessor(unittest.TestCase):
    """Tests pour le traitement du paiement via Stripe (simulé)."""

    def setUp(self):
        self.customer = Customer(
            id="cust1",
            email="client@example.com",
            first_name="Jean",
            last_name="Dupont",
            address={"street": "123 Rue", "city": "Paris"}
        )
        self.payment = Payment(
            id="pay1",
            order_id="order1",
            amount=100.0,
            card_token="tok_visa",
            currency="EUR"
        )

    def test_process_payment_success(self):
        """Test de paiement réussi."""
        status = process_payment(self.payment, self.customer)
        self.assertEqual(status, PaymentStatus.SUCCEEDED)

    def test_process_payment_card_error(self):
        """Test de paiement échoué (carte refusée)."""
        # Simuler une erreur de carte via le mock interne
        original_create = payment_processor.stripe.Charge.create
        payment_processor.stripe.Charge.create = lambda **kwargs: (
            payment_processor.stripe.error.CardError("Carte refusée", "", "", None)
        )
        try:
            with self.assertRaises(PaymentError):
                process_payment(self.payment, self.customer)
        finally:
            payment_processor.stripe.Charge.create = original_create

    def test_process_payment_stripe_error(self):
        """Test de paiement échoué (erreur Stripe)."""
        original_create = payment_processor.stripe.Charge.create
        payment_processor.stripe.Charge.create = lambda **kwargs: (
            payment_processor.stripe.error.StripeError("Erreur Stripe")
        )
        try:
            with self.assertRaises(PaymentError):
                process_payment(self.payment, self.customer)
        finally:
            payment_processor.stripe.Charge.create = original_create

    def test_refund_payment_success(self):
        """Test de remboursement réussi."""
        result = refund_payment("charge123")
        self.assertTrue(result)

    def test_refund_payment_failure(self):
        """Test de remboursement échoué."""
        original_create = payment_processor.stripe.Refund.create
        payment_processor.stripe.Refund.create = lambda **kwargs: (
            payment_processor.stripe.error.StripeError("Erreur Stripe")
        )
        try:
            with self.assertRaises(PaymentError):
                refund_payment("charge123")
        finally:
            payment_processor.stripe.Refund.create = original_create


# Import après la définition de la classe pour éviter les problèmes de référence circulaire
import payment_processor