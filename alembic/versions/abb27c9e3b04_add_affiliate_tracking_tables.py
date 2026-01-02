"""Add affiliate tracking tables

Revision ID: abb27c9e3b04
Revises: e78ea2e7c841
Create Date: 2025-12-08 08:01:59.138802
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'abb27c9e3b04'
down_revision: Union[str, Sequence[str], None] = 'e78ea2e7c841'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Empty migration (placeholder)."""
    pass


def downgrade() -> None:
    """Empty migration (placeholder)."""
    pass
