-- Snowflake Database Setup Script
-- This script sets up the database schema for the FastAPI Snowflake application

CREATE OR REPLACE TABLE users (
    id INT AUTOINCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Insert some sample data for testing
INSERT INTO users (name, email) VALUES
    ('John Doe', 'john.doe@example.com'),
    ('Jane Smith', 'jane.smith@example.com'),
    ('Bob Johnson', 'bob.johnson@example.com'),
    ('Alice Brown', 'alice.brown@example.com'),
    ('Charlie Wilson', 'charlie.wilson@example.com')
ON CONFLICT (email) DO NOTHING;

-- Create an index on email for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Create a view for user statistics (optional)
CREATE OR REPLACE VIEW user_stats AS
SELECT 
    COUNT(*) as total_users,
    COUNT(CASE WHEN created_at >= DATEADD(day, -7, CURRENT_TIMESTAMP()) THEN 1 END) as users_last_7_days,
    COUNT(CASE WHEN created_at >= DATEADD(day, -30, CURRENT_TIMESTAMP()) THEN 1 END) as users_last_30_days,
    MIN(created_at) as first_user_created,
    MAX(created_at) as last_user_created
FROM users;

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE users TO ROLE your_api_role;
-- GRANT SELECT ON VIEW user_stats TO ROLE your_api_role;

-- Example queries for testing user registration logic
/*
-- Test user registration (these queries demonstrate the logic used by the API)

-- Check if user exists
SELECT id, name, email, created_at FROM users WHERE email = 'test@example.com';

-- Register new user (if not exists)
INSERT INTO users (name, email) 
SELECT 'Test User', 'test@example.com' 
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'test@example.com');

-- Update existing user's name
UPDATE users 
SET name = 'Updated Name', updated_at = CURRENT_TIMESTAMP() 
WHERE email = 'test@example.com';

-- Get user statistics
SELECT * FROM user_stats;
*/
