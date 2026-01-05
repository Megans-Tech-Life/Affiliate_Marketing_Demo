from typing import Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from uuid import UUID
from core.database import get_db
from apps.auth.models import User
from apps.auth.security import get_current_user
from .models import AffiliateClick, AffiliateLink
from .services import record_click
from .schemas import AffiliateLinkOut
from .utils import normalize_shop_domain, validate_shop_domain
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/integrations", tags=["Integrations"])

# Generate Affiliate Link for Current User
@router.get("/link", response_model=AffiliateLinkOut)
def generate_affiliate_link(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)):
    
    affiliate_id = current_user.id
    logger.info(f"Generating affiliate link for affiliate_id={affiliate_id}")
    
    affiliate_link = (
        db.query(AffiliateLink)
        .filter(AffiliateLink.affiliate_user_id == affiliate_id)
        .first()
    )

    if not affiliate_link:
        affiliate_link = AffiliateLink(
            affiliate_user_id=affiliate_id,
            created_at=datetime.now(timezone.utc)
        )
    
        db.add(affiliate_link)
        db.commit()
        db.refresh(affiliate_link)

    tracking_url = (
        f"https://yourdomain.com/integrations/redirect"
        f"?utm_source={affiliate_link.id}"
    )

    return AffiliateLinkOut(
        affiliate_link_id=affiliate_link.id,
        affiliate_user_id=affiliate_id,
        tracking_url=tracking_url
    )

# Redirect Affiliate to shop with click tracking
@router.get("/redirect")
def affiliate_redirect(
    utm_source: UUID,
    shop: Optional[str] = None,
    db: Session = Depends(get_db),
):
    logger.info(
        f"Integration redirect received | affiliate_id={utm_source} | raw_shop={shop}"
    )

    affiliate = db.query(User).filter(User.id == utm_source).first()
    if not affiliate:
        logger.warning(f"Affiliate not found: {utm_source}")
        raise HTTPException(status_code=404, detail="Affiliate not found")

    if shop:
        shop = normalize_shop_domain(shop)

        if not validate_shop_domain(shop):
            logger.warning(f"Invalid shop domain: {shop}")
            raise HTTPException(status_code=400, detail="Invalid e-commerce store domain")

        click, referral = record_click(
            db=db,
            affiliate_user_id=utm_source,
            shop_domain=shop,
            utm_source=str(utm_source),
        )

        logger.info(
            f"Click recorded with shop | click_id={click.id} | referral_id={referral.id}"
        )

        redirect_url = f"https://{shop}/apps/your-app"
        logger.info(f"Redirecting to {redirect_url}")
        return RedirectResponse(url=redirect_url)

    # Click-only case
    click = AffiliateClick(
        affiliate_user_id=utm_source,
        utm_source=str(utm_source),
        created_at=datetime.now(timezone.utc),
    )
    db.add(click)
    db.commit()
    db.refresh(click)

    logger.info(f"Click recorded without shop attribution | click_id={click.id}")

    return RedirectResponse(
        url="https://yourdomain.com/integrations/landing"
    )