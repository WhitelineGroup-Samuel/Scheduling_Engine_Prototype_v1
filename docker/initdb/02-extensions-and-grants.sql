-- Enable extensions and sensible default privileges in scheduling_dev
\connect scheduling_dev

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;

-- Ensure our app role owns the public schema (optional but often convenient)
ALTER SCHEMA public OWNER TO scheduler_user;

-- Default privileges: future tables/sequences created by postgres superuser (or current owner)
-- will be accessible to scheduler_user. If you create objects as scheduler_user, it's already fine.
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT
   SELECT, INSERT, UPDATE, DELETE ON TABLES TO scheduler_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT
   USAGE, SELECT ON SEQUENCES TO scheduler_user;

-- Make sure existing objects (if any) are accessible (harmless if none exist yet)
GRANT USAGE ON SCHEMA public TO scheduler_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO scheduler_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO scheduler_user;

-- Repeat for scheduling_test
\connect scheduling_test

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;

ALTER SCHEMA public OWNER TO scheduler_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT
   SELECT, INSERT, UPDATE, DELETE ON TABLES TO scheduler_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT
   USAGE, SELECT ON SEQUENCES TO scheduler_user;

GRANT USAGE ON SCHEMA public TO scheduler_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO scheduler_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO scheduler_user;
