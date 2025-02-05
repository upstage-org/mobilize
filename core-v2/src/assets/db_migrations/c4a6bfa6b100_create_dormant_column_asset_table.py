"""Create Dormant Column Asset Table

Revision ID: c4a6bfa6b100
Revises: c5c56a2bfa78
Create Date: 2025-02-05 13:59:24.026299

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c4a6bfa6b100"
down_revision: Union[str, None] = "c5c56a2bfa78"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "asset", sa.Column("dormant", sa.Boolean(), nullable=True, default=False)
    )


def downgrade() -> None:
    op.drop_column("asset", "dormant")
