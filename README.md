# CRM Sales Pipeline API

## Overview

This project is a **demo backend API** showcasing the design and implementation of a modular, production-style CRM and affiliate tracking system built with **FastAPI**.

It demonstrates real-world SaaS backend patterns including authentication, lead lifecycle management, configurable sales pipelines, affiliate attribution, third-party integrations, transactional tracking, and webhook-safe callbacks.

> ⚠️ **Disclaimer**  
> This repository is a **portfolio/demo project**.  
> It does **not** contain proprietary business logic, client data, secrets, or internal systems from any employer.  
> The architecture is inspired by real-world SaaS platforms but has been generalized for public demonstration.

---

## Authentication

- Register new users: `POST /auth/register`
- Login existing users: `POST /auth/login`
- Retrieve current user info: `GET /auth/me` (JWT required)

JWT-based authentication is used across protected endpoints, with role-aware access for admin-only operations.

---

## Leads Management (CRUD)

- **Create** a new lead: `POST /leads/`
- **Retrieve** all leads for the logged-in user: `GET /leads/`
- **Retrieve** a specific lead: `GET /leads/{lead_id}`
- **Update** a lead: `PUT /leads/{lead_id}`
- **Soft delete** a lead: `DELETE /leads/{lead_id}`

All lead queries are scoped to the authenticated user to ensure proper data isolation.

---

## CRM Pipeline Structure

The sales pipeline is defined using **stage-based configuration files**, enabling flexible, data-driven workflows.

- **Stages** include:  
  `new_account`, `lead`, `demo`, `proposal`, `contract`, `approval`, `customer`, `closed`
- Each stage contains a `substages.json` configuration defining:
  - status
  - description
  - score
  - notes

This approach allows pipeline behavior and scoring logic to be modified **without changing application code**.

---

## Affiliate & Conversion Flow (Demo Highlight)

This project includes a **complete demo affiliate lifecycle**, modeled after real SaaS attribution systems.

### Implemented Flow

Affiliate Link → Redirect Tracking → Install Callback → Lead Attribution → Commission Wallet

### Key Concepts

- Affiliate links are generated per user and expose a stable `affiliate_link_id`
- Redirects track clicks and optionally associate merchant/shop metadata
- Install callbacks:
  - Resolve or create leads
  - Persist affiliate attribution idempotently
- Wallets track commission credits and lifetime earnings
- Derived values (e.g. tracking URLs) are generated dynamically rather than stored

### Conversion Callback

A conversion callback endpoint is wired and intentionally implemented as a **safe no-op**:

- Accepts requests
- Returns `200 OK`
- Does not yet persist purchase or revenue data

This reflects a realistic phased rollout where conversion logic is implemented after install attribution is validated.

---

## Integrations Module

Demonstrates vendor-neutral third-party integration patterns:

- External webhook ingestion
- Identifier normalization and validation
- Attribution to internal entities
- Safe, idempotent processing

---

## Transactions & Wallets

- Commission credits tracked per person
- Wallets auto-create on first commission
- Transaction history retained for auditability
- Aggregated balances maintained for reporting

---

## Performance Tracking

Demonstrates extensible analytics patterns:

- Aggregation of leads, opportunities, and transactions
- User-level performance summaries
- Demo-only compatibility scoring logic

---

## Technology Stack

- **Python 3.11+**
- **FastAPI** – API framework
- **SQLAlchemy + Pydantic** – ORM and data validation
- **PostgreSQL** – Relational database
- **Alembic** – Database migrations
- **Passlib + bcrypt** – Password hashing
- **JWT** – Authentication & authorization

---

## Getting Started

```bash
# Clone the repository
git clone <repo-url>

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/demo_crm

# Run migrations
alembic upgrade head

# Start the API
python -m uvicorn main:app --reload

# Swagger UI available at:
http://127.0.0.1:8000/docs

```
