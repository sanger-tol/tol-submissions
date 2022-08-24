"""setting many columns as null

Revision ID: c93413efb7ec
Revises: 831c4f15fe26
Create Date: 2022-07-18 16:36:04.267939

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c93413efb7ec'
down_revision = '831c4f15fe26'
branch_labels = None
depends_on = None


def upgrade():
    for column in ["genus", "family", "order_or_group", "common_name", "GAL", "GAL_sample_id", "collected_by", "collector_affiliation",
                   "date_of_collection", "collection_location", "decimal_latitude",
                   "decimal_longitude", "habitat", "identified_by", "identifier_affiliation",
                   "voucher_id"]:
        op.alter_column('sample', column,
                existing_type=sa.VARCHAR(),
                nullable=True,
                schema='public')

def downgrade():
    pass
