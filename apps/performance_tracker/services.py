from sqlalchemy.orm import Session
from sqlalchemy import func
from apps.transactions import models as commission_models
from apps.contacts.models import PersonOfContact
from . import models, schemas

# Calculate performance analytics for a given salesperson
def calculate_salesperson_performance(db: Session, salesperson_id):
    total_commission = db.query(func.sum(commission_models.CommissionRecord.amount))\
        .filter(commission_models.CommissionRecord.salesperson_id == salesperson_id)\
        .scalar() or 0.0

    total_commissions = db.query(func.count(commission_models.CommissionRecord.id))\
        .filter(commission_models.CommissionRecord.salesperson_id == salesperson_id)\
        .scalar() or 0

    # Placeholder for future lead/opportunity data
    total_leads = 0
    total_opportunities = 0
    closed_deals = 0
    conversion_rate = 0.0

    return {
        "salesperson_id": str(salesperson_id),
        "total_leads": total_leads,
        "total_opportunities": total_opportunities,
        "closed_deals": closed_deals,
        "conversion_rate": conversion_rate,
        "total_commission": total_commission,
        "total_commission_records": total_commissions
    }

# Suggest salespersons based on client personality type
def personality_match(db: Session, client_personality: str):
    compatibility = {
        "analytical": ["detail-oriented", "methodical"],
        "assertive": ["confident", "decisive"],
        "introverted": ["thoughtful", "reserved"],
        "extroverted": ["energetic", "sociable"]
    }

    client_type = client_personality.lower().strip()
    compatible_traits = compatibility.get(client_type, [])

    if not compatible_traits:
        return {"message": f"No compatible salesperson types found for `{client_personality}` personality."}

    salespeople = db.query(PersonOfContact).filter(PersonOfContact.role == "salesperson").all()

    matches = []
    for s in salespeople:
      if s.personality_type:
          for trait in compatible_traits:
              if trait in s.personality_type.lower():
                  matches.append({
                      "salesperson_id": str(s.id),
                      "salesperson_name": s.name,
                      "salesperson_personality": s.personality_type,
                      "match_reason": f"Compatible with {client_personality} client due to trait `{trait}`"
                  })
                  break
              
              if not matches:
                  return {"message": "No matching salespersons found. Consider assigning manually."}

              return {"client_personality": client_personality, "suggested_salespeople": matches}