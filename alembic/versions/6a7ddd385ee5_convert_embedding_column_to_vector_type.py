"""Convert embedding column to vector type

Revision ID: 6a7ddd385ee5
Revises: 5bd11b5d05f5
Create Date: 2025-08-09 17:26:35.857664

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6a7ddd385ee5"
down_revision: Union[str, Sequence[str], None] = "5bd11b5d05f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Изменяем тип колонки embedding с TEXT на VECTOR(1536)
    # 1536 - это размерность OpenAI embeddings
    op.execute(
        "ALTER TABLE api_embeddings ALTER COLUMN embedding TYPE vector(1536) USING embedding::text::vector"
    )

    # Создаем индекс для быстрого векторного поиска
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_embedding_vector ON api_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем индекс
    op.execute("DROP INDEX IF EXISTS idx_embedding_vector")

    # Возвращаем тип колонки обратно в TEXT
    op.execute("ALTER TABLE api_embeddings ALTER COLUMN embedding TYPE text USING embedding::text")
