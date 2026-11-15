from typing import Tuple
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from models import Order
from exceptions import ConfirmationError
from utils import format_currency


def generate_confirmation_email(order: Order) -> Tuple[str, str]:
    """Génère un email HTML et texte pour une commande donnée.

    Args:
        order: Instance de Order pour laquelle générer l'email.

    Returns:
        Tuple contenant (email_html, email_text).

    Raises:
        ConfirmationError: Si la génération échoue.
    """
    try:
        subject = f"Confirmation de votre commande #{order.id}"
        total = format_currency(order.total_amount, "EUR")

        email_html = f"""
        <html>
            <body>
                <h1>Merci pour votre commande !</h1>
                <p>Bonjour {order.customer.first_name},</p>
                <p>Votre commande #{order.id} a bien été enregistrée.</p>
                <p><strong>Total:</strong> {total}</p>
                <p>Adresse de livraison:</p>
                <p>{order.shipping_address.get('street', '')}<br>
                   {order.shipping_address.get('city', '')} {order.shipping_address.get('zip', '')}</p>
                <p>Nous vous enverrons un email de suivi dès que votre commande sera expédiée.</p>
                <p>Cordialement,<br>L'équipe E-Commerce</p>
            </body>
        </html>
        """

        email_text = f"""
        Merci pour votre commande !
        
        Bonjour {order.customer.first_name},
        
        Votre commande #{order.id} a bien été enregistrée.
        
        Total: {total}
        
        Adresse de livraison:
        {order.shipping_address.get('street', '')}
        {order.shipping_address.get('city', '')} {order.shipping_address.get('zip', '')}
        
        Nous vous enverrons un email de suivi dès que votre commande sera expédiée.
        
        Cordialement,
        L'équipe E-Commerce
        """

        return email_html, email_text

    except Exception as e:
        raise ConfirmationError(f"Échec de la génération de l'email: {e}")


def send_confirmation_email(order: Order, email_html: str, email_text: str) -> str:
    """Envoie l'email de confirmation via SMTP.

    Args:
        order: Instance de Order associée à l'email.
        email_html: Contenu HTML de l'email.
        email_text: Contenu texte de l'email.

    Returns:
        Statut de l'envoi (SENT, FAILED).

    Raises:
        ConfirmationError: Si l'envoi échoue.
    """
    try:
        # Configuration SMTP (à remplacer par des variables d'environnement en production)
        smtp_server = "smtp.example.com"
        smtp_port = 587
        smtp_user = "user@example.com"
        smtp_password = "password"
        from_email = "noreply@example.com"

        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"Confirmation de votre commande #{order.id}"
        msg['From'] = from_email
        msg['To'] = order.customer.email

        # Attacher les versions HTML et texte
        part1 = MIMEText(email_text, 'plain')
        part2 = MIMEText(email_html, 'html')
        msg.attach(part1)
        msg.attach(part2)

        # Envoi via SMTP
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(from_email, [order.customer.email], msg.as_string())

        return "SENT"

    except Exception as e:
        raise ConfirmationError(f"Échec de l'envoi de l'email: {e}")