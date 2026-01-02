# Client routes will be implemented here
# TODO: Add FastAPI routes for client management

from fastapi import APIRouter

router = APIRouter(prefix="/clients", tags=["Clients"])

# TODO: Implement the following endpoints:
# - GET / (list all clients)
# - POST / (create a new client)
# - GET /{client_id} (get specific client)
# - PUT /{client_id} (update client)
# - DELETE /{client_id} (delete client)
# - POST /convert-lead/{lead_id} (convert lead to client)