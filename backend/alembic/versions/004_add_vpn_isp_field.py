"""Add vpn_isp field to click_events for VPN server identification

Revision ID: 004_add_vpn_isp_field
Revises: 003_add_geo_vpn_fields
Create Date: 2026-04-06

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "004_add_vpn_isp_field"
down_revision: Union[str, None] = "003_add_geo_vpn_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "click_events",
        sa.Column("vpn_isp", sa.String(255), nullable=True),
    )
    op.create_index("ix_click_events_vpn_isp", "click_events", ["vpn_isp"])


def downgrade() -> None:
    op.drop_index("ix_click_events_vpn_isp", table_name="click_events")
    op.drop_column("click_events", "vpn_isp")
