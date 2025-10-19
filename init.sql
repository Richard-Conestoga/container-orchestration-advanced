-- Create users table with proper constraints
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on names for faster searches
CREATE INDEX IF NOT EXISTS idx_users_names ON users(first_name, last_name);

-- Insert sample data for testing
INSERT INTO users (first_name, last_name) VALUES
    ('John', 'Doe'),
    ('Jane', 'Smith'),
    ('Alice', 'Johnson')
ON CONFLICT DO NOTHING;