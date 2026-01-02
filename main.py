import apps.leads.scoring

import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')

# Initialize FastAPI app
app = FastAPI(title="CRM Sales Pipeline API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5174",
        "https://demo-frontend.example.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import Routers
from apps.admin.routes import router as admin_router
from apps.accounts.routes import router as accounts_router
from apps.leads.routes import router as leads_router
from apps.opportunities.routes import router as opportunities_router
from apps.contacts.routes import router as contacts_router
from apps.products.routes import router as products_router
from apps.transactions.routes import router as transactions_router
from apps.performance_tracker.routes import router as performance_router
from apps.auth.routes import router as auth_router
from apps.interactions.routes import router as interactions_router
from apps.followups.routes import router as followups_router
from apps.wallet.routes import router as wallet_router
from apps.integrations.routes import router as integrations_router
from apps.integrations.ecommerce_routes import router as ecommerce_router

# Register Routers 
app.include_router(admin_router)
app.include_router(accounts_router)
app.include_router(leads_router)
app.include_router(opportunities_router)
app.include_router(contacts_router)
app.include_router(products_router)
app.include_router(transactions_router)
app.include_router(performance_router)
app.include_router(auth_router)
app.include_router(interactions_router)
app.include_router(followups_router)
app.include_router(wallet_router)
app.include_router(integrations_router)
app.include_router(ecommerce_router)

@app.get("/")
def read_root():
    return {"message": "CRM Sales Pipeline API is running! (Multi-stage lead management system)"}