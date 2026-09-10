import stripe
import os

# SET THIS ON THE SERVER ENV, NOT IN CODE
stripe.api_key = os.getenv("STRIPE_API_KEY", "sk_test_REPLACE_ME")

PRODUCT_NAME = "GhostTrace OSINT Report"
CURRENCY = "usd"
DEFAULT_PRICE = 500  # $5.00 in cents

def get_or_create_customer(email: str):
    customers = stripe.Customer.list(email=email, limit=1).data
    if customers:
        return customers[0]
    return stripe.Customer.create(email=email, description="GhostTrace auto client")

def create_payment_link(customer_email: str, amount_cents: int):
    price = stripe.Price.create(
        unit_amount=amount_cents,
        currency=CURRENCY,
        product_data={"name": PRODUCT_NAME},
    )

    link = stripe.PaymentLink.create(
        line_items=[{"price": price.id, "quantity": 1}],
        metadata={"customer_email": customer_email},
    )
    return link.url

def handle_billing(target_type: str, target_value: str, result: dict):
    # crude mapping: use email if we have one, else fake email from target
    if target_type == "email":
        client_email = target_value
    else:
        client_email = f"{target_type}_{target_value}@ghosttrace.local"

    print(f"[BILLING] preparing charge for {client_email}")

    try:
        customer = get_or_create_customer(client_email)
        print(f"[BILLING] customer {customer.id}")

        link_url = create_payment_link(client_email, DEFAULT_PRICE)
        print(f"[BILLING] payment link: {link_url}")

        # you can later replace this with auto-email sending using your mailer
        print("[BILLING] (TODO) send report + payment link via email")

    except Exception as e:
        print(f"[BILLING ERROR] {e}")
