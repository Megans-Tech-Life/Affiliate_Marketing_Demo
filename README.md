# CRM Sales Pipeline API

## Overview

This project is a **demo backend API** showcasing the design and implementation of a modular, production-style CRM system built with FastAPI.  
It demonstrates real-world SaaS backend patterns such as authentication, lead lifecycle management, configurable sales pipelines, third-party integrations, and transactional tracking.

> ⚠️ **Disclaimer**  
> This repository is a **portfolio/demo project**.  
> It does **not** contain proprietary business logic, client data, secrets, or internal systems from any employer.  
> The architecture is inspired by real-world SaaS systems but has been generalized for public demonstration.

---

## Authentication

- Register new users: `POST /auth/register`
- Login existing users: `POST /auth/login`
- Retrieve current user info: `GET /auth/me` (JWT required)

---

## Leads Management (CRUD)

- **Create** a new lead: `POST /leads/`
- **Retrieve** all leads for the logged-in user: `GET /leads/`
- **Retrieve** a specific lead: `GET /leads/{lead_id}`
- **Update** a lead: `PUT /leads/{lead_id}`
- **Soft delete** a lead: `DELETE /leads/{lead_id}`

---

## CRM Pipeline Structure

The sales pipeline is defined using stage-based configuration files to allow flexible, data-driven workflows.

- **Stages**: `new_account`, `lead`, `demo`, `proposal`, `contract`, `approval`, `customer`, `closed`
- Each stage contains a `substages.json` file defining:
  - status
  - description
  - score
  - notes

This approach allows pipeline behavior and scoring logic to be modified without changing application code.

---

## Integrations Module

Demonstrates handling of third-party integration workflows using generic, vendor-neutral patterns.

- External event ingestion via webhooks
- Attribution and linkage to leads and accounts
- Validation and normalization of external identifiers

---

## Transactions Module

Demonstrates transactional record tracking associated with opportunities and users.

- Create, update, and soft-delete transaction records
- Example calculation logic for transactional values
- Aggregated summaries for reporting and analysis

---

## Performance Tracking

Analyzes user and system performance across the CRM lifecycle.

- Aggregates leads, opportunities, and transactions
- Produces summary metrics per user
- Demonstrates extensible analytics patterns
- Includes optional compatibility scoring between contacts and users (demo-only logic)

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

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies:
   bash
   `pip install -r requirements.txt`
4. Create a .env file with your database configuration (PostgreSQL):
   env
   `DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/demo_crm`
5. Run database migrations (optional for demo):
   bash
   `alembic upgrade head`
6. Start the API:
   bash
   `python -m uvicorn main:app --reload`
7. Open API docs at:
   http://127.0.0.1:8000/docs

## Purpose

This project is intended to demonstrate backend engineering skills including:

API design and routing

Authentication and authorization

Modular service architecture

Database modeling and migrations

Config-driven business workflows

Clean separation of concerns
