"""changed credits type to float

Revision ID: 5e5dd21c3764
Revises: c76574bb1ed1
Create Date: 2026-05-06 11:18:30.251000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5e5dd21c3764"
down_revision: Union[str, Sequence[str], None] = "c76574bb1ed1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table("student_courses") as batch_op:
        batch_op.alter_column(
            "credits_applied",
            existing_type=sa.Integer(),
            type_=sa.Float(),
            existing_nullable=False,
        )


def downgrade():
    with op.batch_alter_table("student_courses") as batch_op:
        batch_op.alter_column(
            "credits_applied",
            existing_type=sa.Float(),
            type_=sa.Integer(),
            existing_nullable=False,
        )
