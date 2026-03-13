"""UTM links and click events tables

Revision ID: 002_utm_tables
Revises: 001_initial
Create Date: 2026-03-13

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "002_utm_tables"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create utm_links table
    op.create_table(
        "utm_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("destination_url", sa.Text, nullable=False),
        sa.Column("short_code", sa.String(20), unique=True, nullable=False),
        sa.Column("utm_source", sa.String(255), nullable=True),
        sa.Column("utm_medium", sa.String(255), nullable=True),
        sa.Column("utm_campaign", sa.String(255), nullable=True),
        sa.Column("utm_term", sa.String(255), nullable=True),
        sa.Column("utm_content", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )
    op.create_index("ix_utm_links_short_code", "utm_links", ["short_code"])
    op.create_index("ix_utm_links_user_created", "utm_links", ["user_id", "created_at"])

    # Create click_events table
    op.create_table(
        "click_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "utm_link_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("utm_links.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("clicked_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text, nullable=True),
        sa.Column("referrer", sa.Text, nullable=True),
        sa.Column("country", sa.String(2), nullable=True),
        sa.Column("device_type", sa.String(50), nullable=True),
        sa.Column("browser", sa.String(100), nullable=True),
    )
    op.create_index("ix_click_events_clicked_at", "click_events", ["clicked_at"])
    op.create_index(
        "ix_click_events_link_clicked", "click_events", ["utm_link_id", "clicked_at"]
    )


def downgrade() -> None:
    op.drop_table("click_events")
    op.drop_table("utm_links")
