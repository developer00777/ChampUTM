"""Add region, city, is_vpn fields to click_events

Revision ID: 003_add_geo_vpn_fields
Revises: 002_utm_tables
Create Date: 2026-03-25

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "003_add_geo_vpn_fields"
down_revision: Union[str, None] = "002_utm_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("click_events", sa.Column("region", sa.String(100), nullable=True))
    op.add_column("click_events", sa.Column("city", sa.String(100), nullable=True))
    op.add_column(
        "click_events",
        sa.Column("is_vpn", sa.Boolean(), server_default="false", nullable=False),
    )
    op.create_index("ix_click_events_country", "click_events", ["country"])
    op.create_index("ix_click_events_vpn", "click_events", ["is_vpn"])


def downgrade() -> None:
    op.drop_index("ix_click_events_vpn", table_name="click_events")
    op.drop_index("ix_click_events_country", table_name="click_events")
    op.drop_column("click_events", "is_vpn")
    op.drop_column("click_events", "city")
    op.drop_column("click_events", "region")
