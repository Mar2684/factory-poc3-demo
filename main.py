#!/usr/bin/env python3
"""
Point d'entrée pour l'exécution des tests ou du service (CLI minimaliste).
"""

import sys
from checkout_service import execute_checkout


def main():
    """CLI minimaliste pour tester le tunnel de paiement."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <test|checkout>")
        sys.exit(1)

    if sys.argv[1] == "test":
        # Exécution des tests unitaires
        import unittest
        loader = unittest.TestLoader()
        suite = loader.discover('tests', pattern='test_*.py')
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        sys.exit(0 if result.wasSuccessful() else 1)

    elif sys.argv[1] == "checkout":
        # Exemple d'exécution du checkout
        order_data = {
            "customer": {
                "email": "client@example.com",
                "first_name": "Jean",
                "last_name": "Dupont",
                "address": {"street": "123 Rue", "city": "Paris", "zip": "75001"}
            },
            "items": [{"id": "prod1", "quantity": 2, "price": 50.0}],
            "total_amount": 100.0,
            "shipping_address": {"street": "123 Rue", "city": "Paris", "zip": "75001"}
        }

        payment_data = {
            "order_id": "",
            "amount": 100.0,
            "card_token": "tok_visa",  # Token Stripe de test
            "currency": "EUR"
        }

        try:
            status = execute_checkout(order_data, payment_data)
            print(f"Checkout terminé avec succès: {status}")
        except Exception as e:
            print(f"Erreur lors du checkout: {e}")
            sys.exit(1)

    else:
        print("Commande inconnue. Utilisez 'test' ou 'checkout'.")
        sys.exit(1)


if __name__ == "__main__":
    main()