from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional
from apps.contacts.models import PersonOfContact
from apps.leads.models import Lead
from apps.opportunities.models import Opportunity
from apps.followups.models import FollowUp

# Helper function to apply date filters
def apply_date_filters(query, model, start_date: Optional[datetime], end_date: Optional[datetime]):
    if start_date and start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)
    if end_date and end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=timezone.utc)
    
    if start_date:
        query = query.filter(model.created_at >= start_date)
    if end_date:
        query = query.filter(model.created_at <= end_date)
    
    return query

# Count functions for each entity
def count_contacts(db: Session, start_date: Optional[datetime], end_date: Optional[datetime]) -> int:
    query = db.query(PersonOfContact)
    query = apply_date_filters(query, PersonOfContact, start_date, end_date)
    return query.count()

def count_leads(db: Session, start_date: Optional[datetime], end_date: Optional[datetime]) -> int:
    query = db.query(Lead)
    query = apply_date_filters(query, Lead, start_date, end_date)
    return query.count()

def count_opportunities(db: Session, start_date: Optional[datetime], end_date: Optional[datetime]) -> int:
    query = db.query(Opportunity)
    query = apply_date_filters(query, Opportunity, start_date, end_date)
    return query.count()

def count_followups(db: Session, start_date: Optional[datetime], end_date: Optional[datetime]) -> int:
    query = db.query(FollowUp)
    query = apply_date_filters(query, FollowUp, start_date, end_date)
    return query.count()

# Wrapper function to get all metrics
def get_all_metrics(db: Session, start_date: Optional[datetime], end_date: Optional[datetime]):
    return {
        "contacts": count_contacts(db, start_date, end_date),
        "leads": count_leads(db, start_date, end_date),
        "opportunities": count_opportunities(db, start_date, end_date),
        "followups": count_followups(db, start_date, end_date),
    }