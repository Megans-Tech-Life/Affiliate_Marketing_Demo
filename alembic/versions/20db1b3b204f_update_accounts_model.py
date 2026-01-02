"""update accounts model

Revision ID: 20db1b3b204f
Revises: 094bc601f6ae
Create Date: 2025-11-18 23:49:48.668061

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# Revision identifiers, used by Alembic.
revision = '20db1b3b204f'
down_revision = '094bc601f6ae'
branch_labels = None
depends_on = None


def upgrade():
    # Add NEW basic info fields
    op.add_column('accounts', sa.Column('company_name', sa.String(length=255), nullable=False))
    op.add_column('accounts', sa.Column('logo_url', sa.String(length=255), nullable=True))
    op.add_column('accounts', sa.Column('company_size', sa.String(length=50), nullable=True))
    op.add_column('accounts', sa.Column('description', sa.String(length=2000), nullable=True))
    op.add_column('accounts', sa.Column('founded_date', sa.Date(), nullable=True))
    op.add_column('accounts', sa.Column('annual_revenue', sa.String(length=100), nullable=True))

    # Add NEW contact fields
    op.add_column('accounts', sa.Column('location', sa.String(length=255), nullable=True))
    op.add_column('accounts', sa.Column('full_address', sa.String(length=255), nullable=True))
    op.add_column('accounts', sa.Column('linkedin_url', sa.String(length=255), nullable=True))
    op.add_column('accounts', sa.Column('twitter_url', sa.String(length=255), nullable=True))
    op.add_column('accounts', sa.Column('instagram_url', sa.String(length=255), nullable=True))

    # Add NEW classification fields
    op.add_column('accounts', sa.Column('account_type', sa.String(length=100), nullable=False))
    op.add_column('accounts', sa.Column('client_type', sa.String(length=100), nullable=False))
    op.add_column('accounts', sa.Column('status', sa.String(length=50), nullable=False))
    op.add_column('accounts', sa.Column('priority', sa.String(length=50), nullable=True))
    op.add_column('accounts', sa.Column('segment', sa.String(length=100), nullable=True))
    op.add_column('accounts', sa.Column('territory', sa.String(length=100), nullable=True))
    op.add_column('accounts', sa.Column('source', sa.String(length=100), nullable=True))
    op.add_column('accounts', sa.Column('tags', postgresql.JSON(astext_type=sa.Text()), nullable=True))

    # Add NEW relationship fields
    op.add_column('accounts', sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('accounts', sa.Column('owner_name', sa.String(length=100), nullable=True))
    op.add_column('accounts', sa.Column('is_subsidiary', sa.Boolean(), nullable=True))

    # Keep existing relationship fields (created_by, is_child_account)
    # No migration needed unless you changed nullable/default

    # Add NEW metrics fields
    op.add_column('accounts', sa.Column('last_activity_date', sa.DateTime(), nullable=True))
    op.add_column('accounts', sa.Column('total_revenue', sa.String(length=255), nullable=True))

    # REMOVE unused JSON fields (old fields)
    op.drop_column('accounts', 'address')
    op.drop_column('accounts', 'social_links')
    op.drop_column('accounts', 'legal_details')


def downgrade():

    # Recreate removed JSON fields
    op.add_column('accounts', sa.Column('address', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('accounts', sa.Column('social_links', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('accounts', sa.Column('legal_details', postgresql.JSON(astext_type=sa.Text()), nullable=True))

    # Drop newly added fields (reverse order recommended)
    op.drop_column('accounts', 'total_revenue')
    op.drop_column('accounts', 'last_activity_date')

    op.drop_column('accounts', 'is_subsidiary')
    op.drop_column('accounts', 'owner_name')
    op.drop_column('accounts', 'owner_id')

    op.drop_column('accounts', 'tags')
    op.drop_column('accounts', 'source')
    op.drop_column('accounts', 'territory')
    op.drop_column('accounts', 'segment')
    op.drop_column('accounts', 'priority')
    op.drop_column('accounts', 'status')
    op.drop_column('accounts', 'client_type')
    op.drop_column('accounts', 'account_type')

    op.drop_column('accounts', 'instagram_url')
    op.drop_column('accounts', 'twitter_url')
    op.drop_column('accounts', 'linkedin_url')
    op.drop_column('accounts', 'full_address')
    op.drop_column('accounts', 'location')

    op.drop_column('accounts', 'annual_revenue')
    op.drop_column('accounts', 'founded_date')
    op.drop_column('accounts', 'description')
    op.drop_column('accounts', 'company_size')
    op.drop_column('accounts', 'logo_url')
    op.drop_column('accounts', 'company_name')
