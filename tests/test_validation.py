import unittest
from validation import validate_customer, validate_order, validate_payment
from exceptions import ValidationError


class TestValidation(unittest.TestCase):
    """Tests pour la validation des données de commande."""

    def test_validate_customer_valid(self):
        """Test de validation d’un client valide."""
        customer_data = {
            "email": "client@example.com",
            "first_name": "Jean",
            "last_name": "Dupont",
            "address": {"street": "123 Rue", "city": "Paris", "zip": "75001"}
        }
        customer = validate_customer(customer_data)
        self.assertEqual(customer.email, "client@example.com")
        self.assertEqual(customer.first_name, "Jean")
        self.assertEqual(customer.last_name, "Dupont")

    def test_validate_customer_invalid_email(self):
        """Test de validation d’un email invalide."""
        customer_data = {
            "email": "invalid-email",
            "first_name": "Jean",
            "last_name": "Dupont",
            "address": {"street": "123 Rue", "city": "Paris"}
        }
        with self.assertRaises(ValidationError):
            validate_customer(customer_data)

    def test_validate_customer_missing_field(self):
        """Test de validation d’un client avec champ manquant."""
        customer_data = {
            "email": "client@example.com",
            "first_name": "Jean",
            # last_name et address manquants
        }
        with self.assertRaises(ValidationError):
            validate_customer(customer_data)

    def test_validate_order_valid(self):
        """Test de validation d’une commande valide."""
        order_data = {
            "customer": {
                "email": "client@example.com",
                "first_name": "Jean",
                "last_name": "Dupont",
                "address": {"street": "123 Rue", "city": "Paris"}
            },
            "items": [{"id": "prod1", "quantity": 2}],
            "total_amount": 100.0,
            "shipping_address": {"street": "123 Rue", "city": "Paris"}
        }
        order = validate_order(order_data)
        self.assertEqual(order.total_amount, 100.0)
        self.assertEqual(len(order.items), 1)

    def test_validate_order_negative_amount(self):
        """Test de validation d’une commande avec montant négatif."""
        order_data = {
            "customer": {
                "email": "client@example.com",
                "first_name": "Jean",
                "last_name": "Dupont",
                "address": {"street": "123 Rue", "city": "Paris"}
            },
            "items": [{"id": "prod1", "quantity": 2}],
            "total_amount": -100.0,
            "shipping_address": {"street": "123 Rue", "city": "Paris"}
        }
        with self.assertRaises(ValidationError):
            validate_order(order_data)

    def test_validate_order_empty_items(self):
        """Test de validation d’une commande avec items vides."""
        order_data = {
            "customer": {
                "email": "client@example.com",
                "first_name": "Jean",
                "last_name": "Dupont",
                "address": {"street": "123 Rue", "city": "Paris"}
            },
            "items": [],
            "total_amount": 100.0,
            "shipping_address": {"street": "123 Rue", "city": "Paris"}
        }
        with self.assertRaises(ValidationError):
            validate_order(order_data)

    def test_validate_payment_valid(self):
        """Test de validation d’un paiement valide."""
        payment_data = {
            "order_id": "order123",
            "amount": 100.0,
            "card_token": "tok_visa",
            "currency": "EUR"
        }
        payment = validate_payment(payment_data)
        self.assertEqual(payment.amount, 100.0)
        self.assertEqual(payment.currency, "EUR")

    def test_validate_payment_negative_amount(self):
        """Test de validation d’un paiement avec montant négatif."""
        payment_data = {
            "order_id": "order123",
            "amount": -100.0,
            "card_token": "tok_visa",
            "currency": "EUR"
        }
        with self.assertRaises(ValidationError):
            validate_payment(payment_data)

    def test_validate_payment_invalid_currency(self):
        """Test de validation d’un paiement avec devise invalide."""
        payment_data = {
            "order_id": "order123",
            "amount": 100.0,
            "card_token": "tok_visa",
            "currency": "XYZ"
        }
        with self.assertRaises(ValidationError):
            validate_payment(payment_data)