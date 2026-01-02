"""Change leads.created_by to UUID

Revision ID: 41e489da78f4
Revises: 38f5d5f835d6
Create Date: 2025-12-17 17:39:13.547461

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '41e489da78f4'
down_revision: Union[str, Sequence[str], None] = '38f5d5f835d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        'leads',
        'created_by',
        type_=sa.UUID(),
        postgresql_using='created_by::uuid',
        existing_nullable=True
    )


def downgrade():
    op.alter_column(
        'leads',
        'created_by',
        type_=sa.VARCHAR(),
        existing_nullable=True
    )

