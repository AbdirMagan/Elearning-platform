# 🐘 PostgreSQL Setup Guide

Complete guide to setting up PostgreSQL for the E-Learning Platform.

## Why PostgreSQL?

✅ **Production-ready** - Industry standard for web applications  
✅ **Better performance** - Faster than SQLite for concurrent users  
✅ **Advanced features** - Full-text search, JSON support, etc.  
✅ **Scalable** - Handles millions of records efficiently  
✅ **ACID compliant** - Data integrity guaranteed  

## Installation

### Windows

1. **Download PostgreSQL**
   - Visit: https://www.postgresql.org/download/windows/
   - Download the installer (version 14 or higher)
   - Run the installer

2. **During Installation:**
   - Set a password for the postgres user (remember this!)
   - Keep default port: 5432
   - Select all components

3. **Verify Installation:**
   ```powershell
   psql --version
   ```

### Mac

```bash
# Using Homebrew
brew install postgresql@14
brew services start postgresql@14
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## Database Setup

### Step 1: Access PostgreSQL

**Windows:**
```powershell
# Open SQL Shell (psql) from Start Menu
# Or use:
psql -U postgres
```

**Mac/Linux:**
```bash
sudo -u postgres psql
```

### Step 2: Create Database and User

```sql
-- Create database
CREATE DATABASE elearning_db;

-- Create user
CREATE USER elearning_user WITH PASSWORD 'your_strong_password_here';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE elearning_db TO elearning_user;

-- Grant schema privileges (PostgreSQL 15+)
\c elearning_db
GRANT ALL ON SCHEMA public TO elearning_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO elearning_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO elearning_user;

-- Exit
\q
```

### Step 3: Test Connection

```bash
psql -U elearning_user -d elearning_db -h localhost
```

If you can connect, you're good to go!

## Project Configuration

### Step 1: Install psycopg2

```powershell
# Activate your virtual environment first
venv\Scripts\activate

# Install PostgreSQL driver
pip install psycopg2-binary
```

### Step 2: Update .env File

Open `.env` and update:

```bash
# Comment out SQLite
# DATABASE_URL=sqlite:///db.sqlite3

# Add PostgreSQL connection
DATABASE_URL=postgresql://elearning_user:your_strong_password_here@localhost:5432/elearning_db
```

**Format:** `postgresql://username:password@host:port/database_name`

**Example with different configurations:**

Local development:
```
DATABASE_URL=postgresql://elearning_user:mypassword123@localhost:5432/elearning_db
```

Production server:
```
DATABASE_URL=postgresql://prod_user:securepwd456@192.168.1.100:5432/elearning_prod
```

### Step 3: Run Migrations

```powershell
# Delete old SQLite database (optional)
del db.sqlite3

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Step 4: Verify

```powershell
python manage.py runserver
```

Visit http://127.0.0.1:8000 and test!

## Common Issues & Solutions

### Issue 1: psycopg2 installation fails

**Solution:**
```powershell
# Try binary version
pip install psycopg2-binary

# Or install build tools and try again
pip install psycopg2
```

### Issue 2: Connection refused

**Solution:**
```powershell
# Check if PostgreSQL is running
# Windows: Services > postgresql-x64-14
# Mac/Linux: sudo systemctl status postgresql

# Check pg_hba.conf allows local connections
# Location: C:\Program Files\PostgreSQL\14\data\pg_hba.conf
# Change: peer/ident to md5 for local connections
```

### Issue 3: Password authentication failed

**Solution:**
```bash
# Reset password
sudo -u postgres psql
ALTER USER elearning_user WITH PASSWORD 'new_password';
\q

# Update .env with new password
```

### Issue 4: Database does not exist

**Solution:**
```sql
-- Create it
sudo -u postgres psql
CREATE DATABASE elearning_db;
\q
```

### Issue 5: Role does not exist

**Solution:**
```sql
sudo -u postgres psql
CREATE USER elearning_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE elearning_db TO elearning_user;
\q
```

## Database Management

### Backup Database

```bash
# Backup
pg_dump -U elearning_user -d elearning_db > backup_$(date +%Y%m%d).sql

# Or with password prompt
pg_dump -U elearning_user -h localhost elearning_db > backup.sql
```

### Restore Database

```bash
# Restore
psql -U elearning_user -d elearning_db < backup.sql
```

### Drop and Recreate Database

```sql
-- Connect to postgres database
psql -U postgres

-- Drop connections
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'elearning_db';

-- Drop database
DROP DATABASE IF EXISTS elearning_db;

-- Recreate
CREATE DATABASE elearning_db;
GRANT ALL PRIVILEGES ON DATABASE elearning_db TO elearning_user;
\q
```

Then run migrations again:
```powershell
python manage.py migrate
python manage.py createsuperuser
```

## Performance Tips

### Add Indexes

```sql
-- Connect to database
psql -U elearning_user -d elearning_db

-- Example: Add index on email (already done in Django)
CREATE INDEX idx_users_email ON users_customuser(email);

-- Check indexes
\di
```

### Vacuum Database

```sql
VACUUM ANALYZE;
```

### Monitor Performance

```sql
-- Show slow queries
SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;

-- Show database size
SELECT pg_size_pretty(pg_database_size('elearning_db'));

-- Show table sizes
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Production Recommendations

### 1. Connection Pooling

Use pgBouncer for connection pooling in production.

### 2. Regular Backups

```bash
# Daily backups (cron job)
0 2 * * * pg_dump -U elearning_user elearning_db > /backups/elearning_$(date +\%Y\%m\%d).sql
```

### 3. Security

```sql
-- Use strong passwords
-- Limit database user permissions
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO elearning_user;

-- Enable SSL connections (pg_hba.conf)
hostssl all all 0.0.0.0/0 md5
```

### 4. Monitoring

- Monitor query performance
- Set up alerts for disk space
- Track connection counts
- Monitor slow queries

## Switching from SQLite to PostgreSQL

### Migration Steps

1. **Backup SQLite data**
   ```powershell
   python manage.py dumpdata > data_backup.json
   ```

2. **Setup PostgreSQL** (follow steps above)

3. **Update .env** with PostgreSQL connection

4. **Run migrations**
   ```powershell
   python manage.py migrate
   ```

5. **Load data**
   ```powershell
   python manage.py loaddata data_backup.json
   ```

## Troubleshooting Checklist

- [ ] PostgreSQL service is running
- [ ] Database exists (check with `\l` in psql)
- [ ] User exists (check with `\du` in psql)
- [ ] User has correct permissions
- [ ] Connection string in .env is correct
- [ ] psycopg2-binary is installed
- [ ] Firewall allows connections to port 5432
- [ ] pg_hba.conf allows md5 authentication

## Quick Reference

```bash
# Common PostgreSQL commands

# Connect to database
psql -U elearning_user -d elearning_db

# List databases
\l

# List users
\du

# List tables
\dt

# Describe table
\d users_customuser

# Execute SQL file
\i script.sql

# Exit
\q

# Check PostgreSQL version
SELECT version();

# Show current database
SELECT current_database();
```

## Resources

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- psycopg2 Documentation: https://www.psycopg.org/docs/
- Django Database Documentation: https://docs.djangoproject.com/en/5.0/ref/databases/

---

**Your database is now production-ready!** 🎉
