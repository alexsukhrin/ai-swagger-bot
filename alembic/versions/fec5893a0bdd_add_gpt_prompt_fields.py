"""add_gpt_prompt_fields

Revision ID: fec5893a0bdd
Revises: 6a7ddd385ee5
Create Date: 2025-08-09 17:42:26.269237

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fec5893a0bdd"
down_revision: Union[str, Sequence[str], None] = "6a7ddd385ee5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - додає поля для GPT-генерованих промптів."""
    # Додаємо поля для прив'язки промптів до endpoint'ів
    op.add_column("prompt_templates", sa.Column("swagger_spec_id", sa.String(36), nullable=True))
    op.add_column("prompt_templates", sa.Column("endpoint_path", sa.String(500), nullable=True))
    op.add_column("prompt_templates", sa.Column("http_method", sa.String(10), nullable=True))
    op.add_column("prompt_templates", sa.Column("resource_type", sa.String(100), nullable=True))
    op.add_column("prompt_templates", sa.Column("tags", sa.JSON, nullable=True))
    op.add_column(
        "prompt_templates", sa.Column("source", sa.String(50), nullable=True, default="manual")
    )
    op.add_column("prompt_templates", sa.Column("priority", sa.Integer, nullable=True, default=1))

    # Додаємо foreign key constraint
    op.create_foreign_key(
        "fk_prompt_templates_swagger_spec",
        "prompt_templates",
        "swagger_specs",
        ["swagger_spec_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # Додаємо індекси для швидкого пошуку
    op.create_index("idx_prompt_swagger_spec", "prompt_templates", ["swagger_spec_id"])
    op.create_index("idx_prompt_endpoint", "prompt_templates", ["endpoint_path", "http_method"])
    op.create_index("idx_prompt_source", "prompt_templates", ["source"])


def downgrade() -> None:
    """Downgrade schema - видаляє поля GPT промптів."""
    # Видаляємо індекси
    op.drop_index("idx_prompt_source", "prompt_templates")
    op.drop_index("idx_prompt_endpoint", "prompt_templates")
    op.drop_index("idx_prompt_swagger_spec", "prompt_templates")

    # Видаляємо foreign key constraint
    op.drop_constraint("fk_prompt_templates_swagger_spec", "prompt_templates", type_="foreignkey")

    # Видаляємо колонки
    op.drop_column("prompt_templates", "priority")
    op.drop_column("prompt_templates", "source")
    op.drop_column("prompt_templates", "tags")
    op.drop_column("prompt_templates", "resource_type")
    op.drop_column("prompt_templates", "http_method")
    op.drop_column("prompt_templates", "endpoint_path")
    op.drop_column("prompt_templates", "swagger_spec_id")
