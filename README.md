# CRM Sales Pipeline API

## Overview

Backend service for managing B2B sales accounts and their progression through a multi-stage CRM-based sales pipeline with affiliate marketing capabilities.

### Authentication

- Register new users `POST /auth/register`
- Login existing users `POST /auth/login`
- Retrieve current user info `GET /auth/me` (JWT required)

### Leads Management (CRUD)

- **Create** a new lead: `POST /leads/`
- **Retrieve** all leads: `GET /leads/`
- **Retrieve** a specific lead: `GET /leads/{lead_id}`
- **Update** a lead: `PUT /leads/{lead_id}`
- **Delete** a lead: `DELETE /leads{lead_id`

## CRM Pipeline Structure

The pipeline is organized into stage-based directories that represent each step of the sales journey.

- **Stages**: new_account, lead, demo, proposal, cotract, approval, customer, closed
- Each stage includes a **substages.json** file containing: status, description, score, notes

## Add-on Features

**Commission Tracker Module**
Tracks and manages sales commissions for each opportunity and salesperson.

- Create, update, and delete commission records.
- Auto-calculates commission based on percentage and opportunity value.
- Provides summary reports (overall and per salesperson).
- Includes optional /init-db endpoint for development table creation.

**Performance Tracker Module** Analyzes salesperson performance and overall productivity while also recommending salespeople to clients with compatible communication styles such as "Assertive".

- Calculates total commissions per salesperson.
- Displays performance summary including leads, opportunities, and conversions.
- Designed to extend easily with real opportunity/lead data.
- Matches personality traits between salespeople and clients based on communication style and behavioral compatibility.
- Personality traits are currently entered manually when creating or updating a Person of Contact record.

## Technology Stack

- **Python 3.11+**
- **FastAPI** API framework
- **SQLAlchemy + Pydantic Schemas** ORM & data validation
- **PostgreSQL** Database
- **Passlib + bcrypt** Password hashing
- **JWT** Authentication
- **Postman** Endpoint testing

## Getting Started

1. Clone the repository
2. Set up a virtual environment
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure your database connection in .env (PostgreSQL)
5. Run the API:

```bash
python -m uvicorn main:app --reload
```

6. Test endpoints using Postman or any API client
