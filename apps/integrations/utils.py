import re
from typing import Optional
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

# Clean and normalize e-commerce store domain
def normalize_shop_domain(shop: str) -> str:
    if not shop:
        return shop
    return shop.strip().lower()

# Validate external e-commerce domain format
def validate_shop_domain(shop: str) -> bool:
    if not shop:
        return False

    pattern = r"^[a-z0-9-]+\.(example|store|shop)\.com$"
    return re.match(pattern, shop.lower()) is not None

# Email sending stub
def send_email(to: str, subject: str, body: str) -> None:
    logger.info(f"EMAIL SENT\nTo: {to}\nSubject: {subject}\nBody:\n{body}")
    pass

# Email message formatting
def format_affiliate_notification(
        event: str,
        shop_domain: str,
        affiliate_user_id: Optional[str] = None
    ) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")

    if event == "install":
        return (
            f"New e-commerce integration completed.\n"
            f"Shop: {shop_domain}\n"
            f"Affiliate: {affiliate_user_id or 'N/A'}\n"
            f"Time: {timestamp}"
        )

    if event == "conversion":
        return (
            f"A referral has converted into a client.\n"
            f"Shop: {shop_domain}\n"
            f"Affiliate: {affiliate_user_id or 'N/A'}\n"
            f"Time: {timestamp}"
        )
    return f"Event '{event}' occurred for shop {shop_domain} at {timestamp}."