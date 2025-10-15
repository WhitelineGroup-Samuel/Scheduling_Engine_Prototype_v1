-- 1) Create the application role if it doesn't exist
DO $$ BEGIN IF NOT EXISTS (
  SELECT
  FROM pg_catalog.pg_roles
  WHERE rolname = 'scheduler_user'
) THEN CREATE ROLE scheduler_user LOGIN PASSWORD 'myschedulerpass';
ALTER ROLE scheduler_user
SET search_path = public;
END IF;
END $$;
-- 2) Create databases at the top level (cannot be inside DO/transaction)
-- Note: CREATE DATABASE does not support IF NOT EXISTS in PostgreSQL.
-- This runs only once during container's first initialization, so it's safe.
CREATE DATABASE scheduling_dev;
CREATE DATABASE scheduling_test;
-- 3) Grant privileges to the app role
GRANT ALL PRIVILEGES ON DATABASE scheduling_dev TO scheduler_user;
GRANT ALL PRIVILEGES ON DATABASE scheduling_test TO scheduler_user;
