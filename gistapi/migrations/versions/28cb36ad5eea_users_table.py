"""users table

Revision ID: 28cb36ad5eea
Revises: 
Create Date: 2022-06-21 15:40:15.898354

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '28cb36ad5eea'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('results',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=32), nullable=True),
    sa.Column('links', sa.String(length=120), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_results_links'), 'results', ['links'], unique=True)
    op.create_index(op.f('ix_results_username'), 'results', ['username'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_results_username'), table_name='results')
    op.drop_index(op.f('ix_results_links'), table_name='results')
    op.drop_table('results')
    # ### end Alembic commands ###
