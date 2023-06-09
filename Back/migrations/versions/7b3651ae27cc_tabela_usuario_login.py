"""Tabela usuario_login

Revision ID: 7b3651ae27cc
Revises: 2af7f555758f
Create Date: 2023-05-23 09:39:48.746950

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b3651ae27cc'
down_revision = '2af7f555758f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('usuario_login',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('senha', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('usuario', sa.Column('avatar', sa.String(), nullable=True))
    op.drop_constraint('usuario_email_key', 'usuario', type_='unique')
    op.drop_constraint('usuario_username_key', 'usuario', type_='unique')
    op.drop_column('usuario', 'email')
    op.drop_column('usuario', 'username')
    op.drop_column('usuario', 'senha')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('usuario', sa.Column('senha', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('usuario', sa.Column('username', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('usuario', sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.create_unique_constraint('usuario_username_key', 'usuario', ['username'])
    op.create_unique_constraint('usuario_email_key', 'usuario', ['email'])
    op.drop_column('usuario', 'avatar')
    op.drop_table('usuario_login')
    # ### end Alembic commands ###
