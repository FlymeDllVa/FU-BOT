"""init

Revision ID: be04415e18e3
Revises: 
Create Date: 2019-12-12 21:59:12.617983

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'be04415e18e3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'vk_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=256), nullable=True),
        sa.Column('update', sa.String(length=256), nullable=True),
        sa.Column('current_name', sa.String(length=256), nullable=True),
        sa.Column('current_id', sa.Integer(), nullable=True),
        sa.Column('schedule_day_date', sa.String(length=256), nullable=True),
        sa.Column('found_id', sa.Integer(), nullable=True),
        sa.Column('found_name', sa.String(length=256), nullable=True),
        sa.Column('found_type', sa.String(length=256), nullable=True),
        sa.Column('subscription_time', sa.String(length=256), nullable=True),
        sa.Column('subscription_days', sa.String(length=256), nullable=True),
        sa.Column('subscription_group', sa.String(length=256), nullable=True),
        sa.Column('show_location', sa.Boolean(), nullable=True),
        sa.Column('show_groups', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_vk_users_id'), 'vk_users', ['id'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    op.drop_index(op.f('ix_vk_users_id'), table_name='vk_users')
    op.drop_table('vk_users')
    # ### end Alembic commands ###
