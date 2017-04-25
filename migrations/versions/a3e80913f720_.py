"""Create note table

Revision ID: a3e80913f720
Revises: None
Create Date: 2017-04-25 17:45:24.573883

"""

# revision identifiers, used by Alembic.
revision = 'a3e80913f720'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('note',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('note_type', sa.String(10), nullable=True),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('rule_id', sa.Integer(), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('updated_on', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['rule_id'], ['rule.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('note')
    # ### end Alembic commands ###
