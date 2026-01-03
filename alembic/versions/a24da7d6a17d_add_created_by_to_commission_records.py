"""add created_by to commission_records

Revision ID: a24da7d6a17d
Revises: 4ebb59d59110
Create Date: 2026-01-02 23:12:37.364298

"""
from typing import Sequence, Union
from sqlalchemy.dialects import postgresql
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a24da7d6a17d'
down_revision: Union[str, Sequence[str], None] = '4ebb59d59110'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "commission_records",
        sa.Column(
            "created_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("commission_records", "created_by")
