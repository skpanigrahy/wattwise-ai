-- WattWise AI Database Initialization Script
-- This script is run when the PostgreSQL container starts for the first time

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- The tables will be created by the application using SQLAlchemy
-- This script is mainly for any initial setup or extensions

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE wattwise_db TO wattwise;

