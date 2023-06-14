"""init

Revision ID: 748587e32a5d
Revises: 
Create Date: 2023-06-21 19:14:04.398595

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '748587e32a5d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('templates',
    sa.Column('tid', sa.String(length=50), nullable=False),
    sa.Column('project', sa.String(length=30), nullable=False),
    sa.Column('version_id', sa.String(length=50), nullable=False),
    sa.Column('template_name', sa.String(length=30), nullable=False),
    sa.Column('template_type', sa.String(length=30), nullable=False),
    sa.Column('template_config', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
    sa.PrimaryKeyConstraint('tid', 'project')
    )
    op.create_table('templates_version',
    sa.Column('tid', sa.String(length=50), nullable=False),
    sa.Column('version_id', sa.String(length=50), nullable=False),
    sa.Column('project', sa.String(length=30), nullable=False),
    sa.Column('template_name', sa.String(length=30), nullable=False),
    sa.Column('template_type', sa.String(length=30), nullable=False),
    sa.Column('template_config', sa.JSON(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
    sa.PrimaryKeyConstraint('tid', 'version_id', 'project')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('templates_version')
    op.drop_table('templates')
    # ### end Alembic commands ###
