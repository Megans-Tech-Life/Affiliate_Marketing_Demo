from dataclasses import dataclass
from core.database import Base

# Admin model to represent single admin user "superadmin"
@dataclass
class Admin:
    admin_id: str
    hashed_password: str

