import unittest
from unittest.mock import patch, MagicMock
from checkout_service import execute_checkout, CheckoutStatus
from exceptions import ValidationError, PaymentError, ConfirmationError


class TestCheckoutService(unittest.TestCase):
    """Tests pour l'orchestration du tunnel de paiement."""

    def setUp(self):
        self.order_data = {
            "customer": {
                "email": "client@example.com",
                "first_name": "Jean",
                "last_name": "Dupont",
                "address": {"street": "123 Rue", "city": "Paris", "zip": "75001"}
            },
            "items": [{"id": "prod1", "quantity": 2}],
            "total_amount": 100.0,
            "shipping_address": {"street": "123 Rue", "city": "Paris", "zip": "75001"}
        }
        self.payment_data = {
            "order_id": "",
            "amount": 100.0,
            "card_token": "tok_visa",
            "currency": "EUR"
        }

    @patch('checkout_service.validate_order')
    @patch('checkout_service.validate_payment')
    @patch('checkout_service.process_payment')
    @patch('checkout_service.generate_confirmation_email')
    @patch('checkout_service.send_confirmation_email')
    def test_execute_checkout_success(
        self, mock_send_email, mock_gen_email, mock_process_payment, mock_validate_payment, mock_validate_order
    ):
        """Test de checkout complet réussi."""
        mock_validate_order.return_value = MagicMock(id="order1")
        mock_validate_payment.return_value = MagicMock(id="pay1", order_id="order1")
        mock_process_payment.return_value = "SUCCEEDED"
        mock_gen_email.return_value = ("<html>...</html>", "texte")
        mock_send_email.return_value = "SENT"

        status = execute_checkout(self.order_data, self.payment_data)
        self.assertEqual(status, CheckoutStatus.CONFIRMED)

    @patch('checkout_service.validate_order')
    def test_execute_checkout_validation_failed(self, mock_validate_order):
        """Test de checkout échoué à la validation."""
        mock_validate_order.side_effect = ValidationError("Email invalide")
        with self.assertRaises(ValidationError):
            execute_checkout(self.order_data, self.payment_data)

    @patch('checkout_service.validate_order')
    @patch('checkout_service.validate_payment')
    @patch('checkout_service.process_payment')
    def test_execute_checkout_payment_failed(self, mock_process_payment, mock_validate_payment, mock_validate_order):
        """Test de checkout échoué au paiement."""
        mock_validate_order.return_value = MagicMock(id="order1")
        mock_validate_payment.return_value = MagicMock(id="pay1", order_id="order1")
        mock_process_payment.side_effect = PaymentError("Carte refusée")

        with self.assertRaises(PaymentError):
            execute_checkout(self.order_data, self.payment_data)

    @patch('checkout_service.validate_order')
    @patch('checkout_service.validate_payment')
    @patch('checkout_service.process_payment')
    @patch('checkout_service.generate_confirmation_email')
    def test_execute_checkout_confirmation_failed(
        self, mock_gen_email, mock_process_payment, mock_validate_payment, mock_validate_order
    ):
        """Test de checkout échoué à la confirmation."""
        mock_validate_order.return_value = MagicMock(id="order1")
        mock_validate_payment.return_value = MagicMock(id="pay1", order_id="order1")
        mock_process_payment.return_value = "SUCCEEDED"
        mock_gen_email.side_effect = ConfirmationError("Échec génération")

        with self.assertRaises(ConfirmationError):
            execute_checkout(self.order_data, self.payment_data)