"""updated hashed_password field in User database

Revision ID: c76574bb1ed1
Revises: 9c393523d53d
Create Date: 2026-05-05 13:07:49.694030

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c76574bb1ed1"
down_revision: Union[str, Sequence[str], None] = "9c393523d53d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "hashed_password",
            existing_type=sa.VARCHAR(),
            type_=sa.LargeBinary(),
            existing_nullable=False,
        )


def downgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "hashed_password",
            existing_type=sa.LargeBinary(),
            type_=sa.VARCHAR(),
            existing_nullable=False,
        )
