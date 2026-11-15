import uuid
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Customer:
    id: str
    email: str
    first_name: str
    last_name: str
    address: Dict


@dataclass
class Order:
    id: str
    customer: Customer
    items: List[Dict]
    total_amount: float
    shipping_address: Dict


@dataclass
class Payment:
    id: str
    order_id: str
    amount: float
    card_token: str
    currency: str = "EUR"


class PaymentStatus:
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"


class ConfirmationStatus:
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"


class CheckoutStatus:
    PENDING = "PENDING"
    VALIDATED = "VALIDATED"
    PAID = "PAID"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
