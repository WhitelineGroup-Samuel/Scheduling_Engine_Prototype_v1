# Setup Guide (Local Development)

## 1. Prerequisites
- macOS (Apple Silicon)
- **Python 3.12**
- **PostgreSQL 16**
- Git, VS Code (Python + Pylance extensions)

## 2. Python 3.12
Choose one:

**Homebrew**
```bash
brew install python@3.12
echo 'export PATH="/opt/homebrew/opt/python@3.12/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
python3 --version  # 3.12.x
```
**pyenv**
```bash
brew install pyenv
pyenv install 3.12.6
pyenv local 3.12.6
python --version
```
Create venv:
```bash
python -m venv .venv
source .venv/bin/activate
```
Select ```.venv``` in VS Code (bottom-right interpreter picker).

## 3. Clone & Repo Basics
```bash
git clone <your-repo-url> Scheduling_Engine_Prototype_v1
cd Scheduling_Engine_Prototype_v1
```

## 4. Databases (manual creation)
Create **dev** and **test** DBs (pick one method):

**psql**
```sql
-- inside psql as a superuser
CREATE DATABASE scheduling_dev;
CREATE DATABASE scheduling_test;
```
**Docker (optional)**
```bash
docker run --name pg16 -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16
# then create the databases via psql or a GUI client
```

## 5. Environment variables
Copy the example and fill values:
```bash
cp .env.example .env
```
Set:
```bash
APP_ENV=dev
EXPORT_DIR=./exports
LOG_LEVEL=INFO
DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/scheduling_dev
TIMEZONE=Australia/Melbourne
LOG_JSON=false
```

## 6. Dependencies (populated later)
When pyproject.toml is ready:
```bash
pip install -e .
pre-commit install
```

## 7. First run (after code generation)
- ```python manage.py check-env```
- ```python manage.py init-db```
- ```python manage.py seed-data```
- ```python run.py```

## 8. Troubleshooting
- **Cannot import modules:** verify interpreter points to ```.venv``` (3.12).
- **DB connection refused:** ensure Postgres is running and credentials match.
- **Migrations not found:** verify ```alembic.ini``` and ```app/db/alembic_env.py``` paths.
