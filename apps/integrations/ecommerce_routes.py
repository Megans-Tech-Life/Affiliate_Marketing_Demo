from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from core.database import get_db
from .services import handle_conversion_callback, handle_install_callback
from .schemas import AffiliateInstallOut, AffiliateConversionOut, InstallCallbackResponse
from .utils import (
    normalize_shop_domain,
    validate_shop_domain
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ecommerce", tags=["E-commerce Integration"])

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging

from core.database import get_db
from .services import handle_install_callback
from .schemas import (
    AffiliateInstallIn,
    InstallCallbackResponse,
    WebhookAck,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ecommerce", tags=["E-commerce Integration"])


@router.post("/install/callback", response_model=InstallCallbackResponse)
def affiliate_install_callback(
    payload: AffiliateInstallIn,
    db: Session = Depends(get_db),
):
    logger.info(
        "E-commerce install callback received | "
        f"affiliate_link_id={payload.affiliate_link_id} | "
        f"lead_id={payload.lead_id} | "
        f"shop={payload.shop_domain}"
    )

    install = handle_install_callback(
        db=db,
        affiliate_link_id=payload.affiliate_link_id,
        lead_id=payload.lead_id,
        shop_domain=payload.shop_domain,
    )

    if not install:
        logger.info(
            "E-commerce install ignored (no persistence required) | "
            f"affiliate_link_id={payload.affiliate_link_id}"
        )
        return WebhookAck(
            type="ack",
            status="ok",
            message="E-commerce install ignored",
        )

    logger.info(
        "E-commerce install completed successfully | "
        f"install_id={install.id}"
    )
    return AffiliateInstallOut.model_validate(install)
    
@router.get("/conversion/callback", response_model=AffiliateConversionOut)
def ecommerce_conversion_callback(shop: str, db: Session = Depends(get_db)):
    logger.info(f"E-commerce conversion callback received | raw_shop={shop}")

    shop = normalize_shop_domain(shop)

    if not validate_shop_domain(shop):
        logger.warning(f"Invalid shop domain received in conversion callback: {shop}")
        raise HTTPException(status_code=400, detail="Invalid e-commerce store domain")

    try:
        result = handle_conversion_callback(db=db, shop_domain=shop)
        logger.info(f"E-commerce conversion callback processed | shop={shop}")
        return result

    except ValueError as e:
        logger.warning(f"Conversion callback validation error | shop={shop} | error={str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        logger.exception(f"Unexpected error during conversion callback | shop={shop}")
        raise HTTPException(status_code=500, detail="Internal server error")