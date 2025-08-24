-- Ініціалізація реальної PostgreSQL бази з pgvector для тестування
-- Цей скрипт виконується автоматично при створенні контейнера

-- Включаємо pgvector розширення
CREATE EXTENSION IF NOT EXISTS vector;

-- Створюємо схему для тестування
CREATE SCHEMA IF NOT EXISTS test_schema;

-- Створюємо таблицю для embeddings
CREATE TABLE IF NOT EXISTS test_embeddings (
    id SERIAL PRIMARY KEY,
    text_content TEXT NOT NULL,
    metadata JSONB,
    embedding vector(1536),  -- Стандартна розмірність для OpenAI embeddings
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Створюємо таблицю для документів
CREATE TABLE IF NOT EXISTS test_documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255),
    content TEXT NOT NULL,
    document_type VARCHAR(100),
    source_url VARCHAR(500),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Створюємо таблицю для Swagger специфікацій
CREATE TABLE IF NOT EXISTS test_swagger_specs (
    id SERIAL PRIMARY KEY,
    spec_name VARCHAR(255) NOT NULL,
    spec_version VARCHAR(50),
    spec_content JSONB NOT NULL,
    parsed_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Створюємо таблицю для API endpoints
CREATE TABLE IF NOT EXISTS test_api_endpoints (
    id SERIAL PRIMARY KEY,
    path VARCHAR(500) NOT NULL,
    method VARCHAR(10) NOT NULL,
    summary TEXT,
    description TEXT,
    parameters JSONB,
    responses JSONB,
    tags TEXT[],
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Створюємо таблицю для схем даних
CREATE TABLE IF NOT EXISTS test_data_schemas (
    id SERIAL PRIMARY KEY,
    schema_name VARCHAR(255) NOT NULL,
    schema_type VARCHAR(100),
    properties JSONB,
    required_fields TEXT[],
    examples JSONB,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Створюємо індекси для швидкого пошуку
CREATE INDEX IF NOT EXISTS idx_test_embeddings_text ON test_embeddings USING gin(to_tsvector('english', text_content));
CREATE INDEX IF NOT EXISTS idx_test_embeddings_metadata ON test_embeddings USING gin(metadata);
CREATE INDEX IF NOT EXISTS idx_test_embeddings_embedding ON test_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX IF NOT EXISTS idx_test_documents_content ON test_documents USING gin(to_tsvector('english', content));
CREATE INDEX IF NOT EXISTS idx_test_documents_type ON test_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_test_documents_metadata ON test_documents USING gin(metadata);

CREATE INDEX IF NOT EXISTS idx_test_swagger_specs_name ON test_swagger_specs(spec_name);
CREATE INDEX IF NOT EXISTS idx_test_swagger_specs_content ON test_swagger_specs USING gin(spec_content);

CREATE INDEX IF NOT EXISTS idx_test_api_endpoints_path ON test_api_endpoints(path);
CREATE INDEX IF NOT EXISTS idx_test_api_endpoints_method ON test_api_endpoints(method);
CREATE INDEX IF NOT EXISTS idx_test_api_endpoints_tags ON test_api_endpoints USING gin(tags);

CREATE INDEX IF NOT EXISTS idx_test_data_schemas_name ON test_data_schemas(schema_name);
CREATE INDEX IF NOT EXISTS idx_test_data_schemas_type ON test_data_schemas(schema_type);

-- Створюємо функцію для оновлення updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Створюємо тригери для автоматичного оновлення updated_at
CREATE TRIGGER update_test_embeddings_updated_at BEFORE UPDATE ON test_embeddings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_test_swagger_specs_updated_at BEFORE UPDATE ON test_swagger_specs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Створюємо функцію для пошуку подібних embeddings
CREATE OR REPLACE FUNCTION search_similar_embeddings(
    query_embedding vector(1536),
    similarity_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id int,
    text_content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.text_content,
        e.metadata,
        1 - (e.embedding <=> query_embedding) as similarity
    FROM test_embeddings e
    WHERE 1 - (e.embedding <=> query_embedding) > similarity_threshold
    ORDER BY e.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Створюємо функцію для гібридного пошуку
CREATE OR REPLACE FUNCTION hybrid_search(
    query_text text,
    query_embedding vector(1536),
    metadata_filter jsonb DEFAULT '{}',
    similarity_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id int,
    text_content text,
    metadata jsonb,
    text_similarity float,
    vector_similarity float,
    combined_score float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.text_content,
        e.metadata,
        ts_rank(to_tsvector('english', e.text_content), plainto_tsquery('english', query_text)) as text_similarity,
        1 - (e.embedding <=> query_embedding) as vector_similarity,
        (ts_rank(to_tsvector('english', e.text_content), plainto_tsquery('english', query_text)) +
         (1 - (e.embedding <=> query_embedding))) / 2 as combined_score
    FROM test_embeddings e
    WHERE
        (metadata_filter = '{}' OR e.metadata @> metadata_filter)
        AND (1 - (e.embedding <=> query_embedding)) > similarity_threshold
    ORDER BY combined_score DESC
    LIMIT match_count;
END;
$$;

-- Вставляємо тестові дані
INSERT INTO test_embeddings (text_content, metadata, embedding) VALUES
(
    'API для створення категорій товарів',
    '{"type": "endpoint", "method": "POST", "path": "/api/categories", "description": "Створення нової категорії товарів"}',
    '[0.1, 0.2, 0.3, 0.4, 0.5]'::vector
),
(
    'Отримання списку всіх категорій',
    '{"type": "endpoint", "method": "GET", "path": "/api/categories", "description": "Отримання списку всіх категорій"}',
    '[0.2, 0.3, 0.4, 0.5, 0.6]'::vector
),
(
    'Оновлення існуючої категорії',
    '{"type": "endpoint", "method": "PATCH", "path": "/api/categories/{id}", "description": "Оновлення існуючої категорії"}',
    '[0.3, 0.4, 0.5, 0.6, 0.7]'::vector
);

INSERT INTO test_documents (title, content, document_type, metadata) VALUES
(
    'API Документація',
    'Документація API для роботи з категоріями товарів в e-commerce системі',
    'api_docs',
    '{"version": "1.0", "author": "Test User"}'
),
(
    'Інструкція користувача',
    'Інструкція по використанню API для розробників',
    'user_guide',
    '{"audience": "developers", "difficulty": "intermediate"}'
);

-- Створюємо користувача для тестування
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'test_user') THEN
        CREATE ROLE test_user LOGIN PASSWORD 'change_this_password_in_production';
    END IF;
END
$$;

-- Надаємо права тестовому користувачу
GRANT USAGE ON SCHEMA test_schema TO test_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA test_schema TO test_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA test_schema TO test_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA test_schema TO test_user;

-- Виводимо інформацію про створену базу
SELECT
    'База даних створена успішно!' as status,
    current_database() as database_name,
    current_user as current_user,
    version() as postgres_version;

-- Перевіряємо pgvector
SELECT
    'pgvector розширення' as extension_name,
    extversion as version
FROM pg_extension
WHERE extname = 'vector';

-- Показуємо створені таблиці
SELECT
    schemaname,
    tablename,
    tableowner
FROM pg_tables
WHERE schemaname = 'test_schema'
ORDER BY tablename;
