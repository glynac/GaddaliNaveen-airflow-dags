# Airflow Docker Environment

## Prerequisites
- Docker installed
- Docker Compose installed

## Start the environment
```bash
docker compose up -d
```
## Stop the environment
```bash
docker compose down
```

## Access Airflow UI
- URL: http://localhost:8080
- Username: airflow
- Password: airflow

## Notes
- All DAGs should be placed inside the dags/ folder
- PostgreSQL runs on port 5433 for local development
- Environment variables are defined in .env.example