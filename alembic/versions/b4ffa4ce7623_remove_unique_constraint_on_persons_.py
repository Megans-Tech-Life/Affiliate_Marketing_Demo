"""remove unique constraint on persons.user_id

Revision ID: b4ffa4ce7623
Revises: 5067587f2f00
Create Date: 2026-01-02 18:50:15.918593

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4ffa4ce7623'
down_revision: Union[str, Sequence[str], None] = '5067587f2f00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_constraint(
        "persons_user_id_key",
        "persons",
        type_="unique",
    )

def downgrade():
    op.create_unique_constraint(
        "persons_user_id_key",
        "persons",
        ["user_id"],
    )
