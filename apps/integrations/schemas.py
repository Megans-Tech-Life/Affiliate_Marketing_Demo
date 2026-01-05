from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from typing import Literal, Union, Annotated
from pydantic import Field

class AffiliateClickOut(BaseModel):
    id: UUID
    affiliate_user_id: UUID
    shop_domain: str
    utm_source: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AffiliateReferralOut(BaseModel):
    id: UUID
    affiliate_user_id: UUID
    shop_domain: str
    status: str
    last_click_id: Optional[UUID] = None
    last_clicked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class AffiliateInstallIn(BaseModel):
    affiliate_link_id: UUID
    lead_id: Optional[UUID] = None
    shop_domain: Optional[str] = None

    class Config:
        from_attributes = True
    
class AffiliateInstallOut(BaseModel):
    type: Literal["install"] = "install"
    id: UUID
    affiliate_user_id: Optional[UUID]
    affiliate_link_id: UUID
    lead_id: UUID
    shop_domain: Optional[str] = None
    client_account_id: Optional[UUID] = None
    installed_at: datetime
    converted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AffiliateConversionOut(BaseModel):
   status: str
   shop_domain: Optional[str] = None
   affiliate_user_id: Optional[UUID] = None

class AffiliateLinkOut(BaseModel):
    affiliate_link_id: UUID
    affiliate_user_id: UUID
    tracking_url: str

class WebhookAck(BaseModel):
    type: Literal["ack"] = "ack"
    status: str
    message: str

InstallCallbackResponse = Annotated[
    Union[AffiliateInstallOut, WebhookAck],
    Field(discriminator="type"),
]