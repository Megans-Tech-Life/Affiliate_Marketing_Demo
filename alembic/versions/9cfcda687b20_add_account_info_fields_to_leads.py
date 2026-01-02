"""add account info fields to leads

Revision ID: 9cfcda687b20
Revises: fa45fde16d4a
Create Date: 2025-12-12 09:46:55.398558

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9cfcda687b20'
down_revision: Union[str, Sequence[str], None] = 'fa45fde16d4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "leads",
        sa.Column("company_name", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "leads",
        sa.Column("industry", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "leads",
        sa.Column("company_size", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "leads",
        sa.Column("website", sa.String(length=255), nullable=True),
    )


def downgrade():
    op.drop_column("leads", "website")
    op.drop_column("leads", "company_size")
    op.drop_column("leads", "industry")
    op.drop_column("leads", "company_name")