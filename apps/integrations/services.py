from sqlalchemy.orm import Session
from datetime import datetime, timezone
from uuid import UUID
import logging

from apps.leads.models import Lead
from .models import AffiliateClick, AffiliateLink, AffiliateReferral, AffiliateInstall
from apps.accounts.models import Account
from .utils import (
    normalize_shop_domain,
    validate_shop_domain,
    send_email,
    format_affiliate_notification
)

logger = logging.getLogger(__name__)

# Click handler to record affiliate click and referral
def record_click(db: Session, affiliate_user_id: UUID, shop_domain: str, utm_source: str = None):
    logger.info(f"Recording affiliate click | affiliate_id={affiliate_user_id} | shop={shop_domain}")
    # Normalize & validate shop domain
    shop_domain = normalize_shop_domain(shop_domain)
    if not validate_shop_domain(shop_domain):
        raise ValueError("Invalid e-commerce store domain format")

    # Create click record
    click = AffiliateClick(
        affiliate_user_id=affiliate_user_id,
        shop_domain=shop_domain,
        utm_source=utm_source,
        created_at=datetime.now(timezone.utc)
    )
    db.add(click)
    db.commit()
    db.refresh(click)

    # Retrieve or create referral
    referral = (
        db.query(AffiliateReferral)
        .filter_by(affiliate_user_id=affiliate_user_id, shop_domain=shop_domain)
        .first()
    )

    if referral:
        logger.info(f"Existing referral found | referral_id={referral.id}")
        referral.last_click_id = click.id
        referral.last_clicked_at = datetime.now(timezone.utc)
        referral.updated_at = datetime.now(timezone.utc)
    else:
        logger.info("No referral found — creating new referral")
        referral = AffiliateReferral(
            affiliate_user_id=affiliate_user_id,
            shop_domain=shop_domain,
            last_click_id=click.id,
            last_clicked_at=datetime.now(timezone.utc),
            status="pending",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.add(referral)

    db.commit()
    logger.info(f"Referral resolved | referral_id={referral.id} | status={referral.status}")
    db.refresh(referral)
    return click, referral

# Get referral by shop domain
def get_referral_by_shop(db: Session, shop_domain: str):
    shop_domain = normalize_shop_domain(shop_domain)
    return (
        db.query(AffiliateReferral)
        .filter_by(shop_domain=shop_domain)
        .order_by(AffiliateReferral.updated_at.desc())
        .first()
    )

# Install callback to handle install event and notify
def handle_install_callback(
    db: Session,
    affiliate_link_id: UUID,
    shop_domain: str | None = None,
    lead_id: UUID | None = None,
):
    logger.info(
        "Affiliate install received | "
        f"affiliate_link_id={affiliate_link_id} | "
        f"lead_id={lead_id} | shop={shop_domain}"
    )

    # Resolve affiliate link (source of truth)
    affiliate_link = (
        db.query(AffiliateLink)
        .filter_by(id=affiliate_link_id)
        .first()
    )

    if not affiliate_link:
        logger.warning(
            f"Affiliate install ignored — affiliate link not found | "
            f"affiliate_link_id={affiliate_link_id}"
        )
        return None

    affiliate_user_id = affiliate_link.affiliate_user_id

    # Resolve or create lead
    lead = None
    if lead_id:
        lead = db.query(Lead).filter_by(id=lead_id).first()
        if not lead:
            logger.warning(f"Provided lead_id not found | lead_id={lead_id}")
    if not lead:
        lead = Lead(
            source="affiliate",
            affiliate_link_id=affiliate_link.id,
            created_at=datetime.now(timezone.utc),
        )
        db.add(lead)
        db.commit()
        db.refresh(lead)

        logger.info(f"New lead created from affiliate install | lead_id={lead.id}")

    # Ensure attribution is correct
    if lead.affiliate_link_id is None:
        lead.affiliate_link_id = affiliate_link.id
        db.commit()
        logger.info(f"Lead attributed to affiliate link | lead_id={lead.id} | affiliate_link_id={affiliate_link.id}")

    # Idempotency check
    existing_install = (
        db.query(AffiliateInstall)
        .filter_by(affiliate_link_id=affiliate_link.id, lead_id=lead.id)
        .first()
    )

    if existing_install:
        logger.info(
            "Affiliate install already exists — skipping create | "
            f"install_id={existing_install.id}"
        )
        return existing_install

    # Create install record
    install = AffiliateInstall(
        affiliate_user_id=affiliate_user_id,
        affiliate_link_id=affiliate_link.id,
        lead_id=lead.id,
        shop_domain=shop_domain,
        installed_at=datetime.now(timezone.utc),
    )
    db.add(install)
    db.commit()
    db.refresh(install)

    logger.info(
        "Affiliate install persisted successfully | "
        f"install_id={install.id} | "
        f"affiliate_link_id={affiliate_link.id} | "
        f"lead_id={lead.id} | "
        f"shop={shop_domain}"
    )
# Temporarily disabled email notifications until install/conversion 
# flows are successfully tested
# Install email notifications
#    admin_body = format_affiliate_notification(
#        event="install",
#        shop_domain=shop_domain,
#        affiliate_user_id=str(affiliate_user_id)
#    )
#    # TODO: Replace with real admin email
#    send_email("admin@placeholder.com", "New E-commerce Install", admin_body)

#    if affiliate_user_id:
#        affiliate_body = format_affiliate_notification(
#            event="install",
#            shop_domain=shop_domain,
#            affiliate_user_id=str(affiliate_user_id)
#        )
        # TODO: Replace with real affiliate email
#        send_email("affiliate@placeholder.com", "Your Referral Installed", affiliate_body)
    return install

# Conversion handler to record conversion event and notify
def handle_conversion_callback(db: Session, shop_domain: str):
    
    shop_domain = normalize_shop_domain(shop_domain)
    if not validate_shop_domain(shop_domain):
        raise ValueError("Invalid e-commerce store domain format")

    referral = get_referral_by_shop(db, shop_domain)

    if referral:
        affiliate_user_id = referral.affiliate_user_id
        referral.status = "converted"
        referral.updated_at = datetime.now(timezone.utc)
        db.commit()
        logger.info(f"Conversion attributed to affiliate {affiliate_user_id} for shop {shop_domain}")
    else:
        affiliate_user_id = None
        logger.warning(f"No referral found for conversion for shop {shop_domain}")

    # Get latest install
    install = (
        db.query(AffiliateInstall)
        .filter_by(shop_domain=shop_domain)
        .order_by(AffiliateInstall.installed_at.desc())
        .first()
    )

    if install:
        install.converted_at = datetime.now(timezone.utc)
        db.commit()

        # Send conversion email notifications
        admin_body = format_affiliate_notification(
            event="conversion",
            shop_domain=shop_domain,
            affiliate_user_id=str(affiliate_user_id)
        )
        # TODO: Replace with real admin email
        send_email("admin@placeholder.com", "Referral Converted", admin_body)

        if affiliate_user_id:
            affiliate_body = format_affiliate_notification(
                event="conversion",
                shop_domain=shop_domain,
                affiliate_user_id=str(affiliate_user_id)
            )
            # TODO: Replace with real affiliate email
            send_email("affiliate@placeholder.com", "Your Referral Converted!", affiliate_body)
        return {"status": "conversion recorded"}

    logger.warning(f"No install record found for conversion for shop {shop_domain}")
    return {"status": "conversion recorded but install not found"}