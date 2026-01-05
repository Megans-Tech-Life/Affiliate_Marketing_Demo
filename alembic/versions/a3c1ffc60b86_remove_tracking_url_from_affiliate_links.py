"""remove tracking_url from affiliate_links

Revision ID: a3c1ffc60b86
Revises: a24da7d6a17d
Create Date: 2026-01-04 23:33:31.501753

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3c1ffc60b86'
down_revision: Union[str, Sequence[str], None] = 'a24da7d6a17d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_column("affiliate_links", "tracking_url")


def downgrade():
    op.add_column(
        "affiliate_links",
        sa.Column("tracking_url", sa.String(), nullable=False)
    )
