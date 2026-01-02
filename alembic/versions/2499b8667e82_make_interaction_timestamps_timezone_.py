"""Make interaction timestamps timezone-aware

Revision ID: 2499b8667e82
Revises: 7ac134c0adc7
Create Date: 2025-12-15 16:22:49.287025

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2499b8667e82'
down_revision: Union[str, Sequence[str], None] = '7ac134c0adc7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        "interactions",
        "occurred_at",
        type_=sa.DateTime(timezone=True),
        postgresql_using="occurred_at AT TIME ZONE 'UTC'",
        existing_type=sa.DateTime(),
        nullable=False,
    )

    op.alter_column(
        "interactions",
        "created_at",
        type_=sa.DateTime(timezone=True),
        postgresql_using="created_at AT TIME ZONE 'UTC'",
        existing_type=sa.DateTime(),
        nullable=False,
    )

    op.alter_column(
        "interactions",
        "updated_at",
        type_=sa.DateTime(timezone=True),
        postgresql_using="updated_at AT TIME ZONE 'UTC'",
        existing_type=sa.DateTime(),
        nullable=False,
    )


def downgrade():
    op.alter_column(
        "interactions",
        "occurred_at",
        type_=sa.DateTime(),
        postgresql_using="occurred_at::timestamp",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )

    op.alter_column(
        "interactions",
        "created_at",
        type_=sa.DateTime(),
        postgresql_using="created_at::timestamp",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )

    op.alter_column(
        "interactions",
        "updated_at",
        type_=sa.DateTime(),
        postgresql_using="updated_at::timestamp",
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )