"""added databases for all clases

Revision ID: fa067ccdcb98
Revises: f603871ac87d
Create Date: 2021-03-05 14:57:03.729003

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fa067ccdcb98'
down_revision = 'f603871ac87d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ticket',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('screen',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ticket_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['ticket_id'], ['ticket.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('movie',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=80), nullable=True),
    sa.Column('blurb', sa.String(length=500), nullable=True),
    sa.Column('certificate', sa.String(length=20), nullable=True),
    sa.Column('runtime', sa.DateTime(), nullable=True),
    sa.Column('screen_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['screen_id'], ['screen.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('seat',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('availability', sa.Boolean(), nullable=True),
    sa.Column('screen_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['screen_id'], ['screen.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('user', sa.Column('age', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'age')
    op.drop_table('seat')
    op.drop_table('movie')
    op.drop_table('screen')
    op.drop_table('ticket')
    # ### end Alembic commands ###