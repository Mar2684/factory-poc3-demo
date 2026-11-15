from typing import Dict
from models import Customer, Order, Payment
from exceptions import ValidationError


def validate_customer(customer_data: Dict) -> Customer:
    """Valide un objet Customer et retourne une instance de Customer si valide.

    Args:
        customer_data: Dictionnaire contenant les données du client.

    Returns:
        Instance de Customer valide.

    Raises:
        ValidationError: Si les données sont invalides (email invalide, champs manquants).
    """
    required_fields = ["email", "first_name", "last_name", "address"]
    for field in required_fields:
        if field not in customer_data:
            raise ValidationError(f"Champ manquant: {field}")

    email = customer_data["email"]
    if "@" not in email or "." not in email:
        raise ValidationError("Email invalide")

    return Customer(
        id="",  # ID généré plus tard si nécessaire
        email=customer_data["email"],
        first_name=customer_data["first_name"],
        last_name=customer_data["last_name"],
        address=customer_data["address"],
    )


def validate_order(order_data: Dict) -> Order:
    """Valide un dictionnaire order_data et retourne une instance de Order si valide.

    Args:
        order_data: Dictionnaire contenant les données de la commande.

    Returns:
        Instance de Order valide.

    Raises:
        ValidationError: Si les données sont invalides (montant négatif, items vides, adresse invalide).
    """
    required_fields = ["customer", "items", "total_amount", "shipping_address"]
    for field in required_fields:
        if field not in order_data:
            raise ValidationError(f"Champ manquant: {field}")

    if order_data["total_amount"] <= 0:
        raise ValidationError("Montant total doit être positif")

    if not order_data["items"]:
        raise ValidationError("La liste des items ne peut pas être vide")

    try:
        customer = validate_customer(order_data["customer"])
    except ValidationError as e:
        raise ValidationError(f"Validation du client échouée: {e}")

    return Order(
        id="",  # ID généré plus tard si nécessaire
        customer=customer,
        items=order_data["items"],
        total_amount=order_data["total_amount"],
        shipping_address=order_data["shipping_address"],
    )


def validate_payment(payment_data: Dict) -> Payment:
    """Valide les données de paiement et retourne une instance de Payment.

    Args:
        payment_data: Dictionnaire contenant les données de paiement.

    Returns:
        Instance de Payment valide.

    Raises:
        ValidationError: Si les données sont invalides (carte expirée, montant incohérent).
    """
    required_fields = ["order_id", "amount", "card_token", "currency"]
    for field in required_fields:
        if field not in payment_data:
            raise ValidationError(f"Champ manquant: {field}")

    if payment_data["amount"] <= 0:
        raise ValidationError("Montant du paiement doit être positif")

    if payment_data["currency"] not in ["EUR", "USD", "GBP"]:
        raise ValidationError("Devise non supportée")

    return Payment(
        id="",  # ID généré plus tard si nécessaire
        order_id=payment_data["order_id"],
        amount=payment_data["amount"],
        card_token=payment_data["card_token"],
        currency=payment_data.get("currency", "EUR"),
    )