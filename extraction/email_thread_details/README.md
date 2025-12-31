# Email Thread Details – Ingestion Pipeline

## Dataset Overview

**Dataset name:** `email_thread_details`

**Purpose:**  
This dataset contains email thread summary information. The pipeline ingests local CSV files, validates them against a schema contract, and loads clean records into a PostgreSQL table using Apache Airflow.

**CSV location:**  
extraction/email_thread_details/sample_data/

**Target PostgreSQL table:**  
public.email_thread_details

## Dataset Configuration Files

This dataset is fully configuration-driven. The following files define how the pipeline behaves:

| File | Description |
|-----|------------|
| `MANIFEST.md` | Dataset metadata including name, CSV path, and target table |
| `config/schema_expected.yaml` | Schema contract defining columns, data types, and nullability |
| `config/create_table.sql` | PostgreSQL table DDL used during data loading |
| `sample_data/email_thread_details.csv` | Sample CSV used for testing and validation |
| `dags/email_thread_details_ingest.py` | Airflow DAG that performs ingestion, validation, and loading |

---

## Required Environment Variables

All database credentials and connection details are externalized and loaded via environment variables.

Reference file: .env.sample


The following variables must be set:

PG_HOST
PG_PORT
PG_DB
PG_USER
PG_PASSWORD

## How to Run the Pipeline

### Start Airflow Environment

From the Airflow project directory, start the services using Docker Compose:

```bash
docker compose up -d
```

Access the Airflow UI at: http://localhost:8080

Login credentials:
Username: airflow
Password: airflow

### Trigger the DAG

1. Open the Airflow UI
2. Locate the DAG: email_thread_details_ingest
3. Enable the DAG
4. Trigger a manual run

## DAG Overview

**DAG name:**
`email_thread_details_ingest`


### Task Flow

check_file_exists
      ↓
validate_schema
      ↓
transform_data
      ↓
load_to_postgres


### Task Descriptions

- **check_file_exists**  
  Verifies the CSV exists in `sample_data/`.

- **validate_schema**  
  Validates CSV structure against `schema_expected.yaml`.  
  Fails the DAG on mismatch.

- **transform_data**  
  Strips whitespace, handles null values, and skips rows already marked as `done`.

- **load_to_postgres**  
  Creates the target table if required and loads cleaned data into PostgreSQL.

## Troubleshooting

### Schema Mismatch Errors
**Symptoms:**
- DAG fails at `validate_schema`
- Errors about missing or unexpected columns

**Resolution:**
- Verify CSV header matches `schema_expected.yaml`
- Update schema file if dataset structure has changed

---

### Missing CSV File
**Symptoms:**
- DAG fails at `check_file_exists`
- File not found error

**Resolution:**
- Confirm CSV exists under: sample_data/

- Ensure file name matches the manifest

---

### PostgreSQL Connection Errors
**Symptoms:**
- DAG fails at `load_to_postgres`
- Connection refused or authentication errors

**Resolution:**
- Verify values in `.env`
- Restart Docker Compose after changes:
```bash
docker compose down
docker compose up -d
```
### Resetting DAG Runs / Reloading Data

**Steps:**
1. Clear task instances from the Airflow UI  
2. Optionally truncate the target PostgreSQL table  
3. Trigger the DAG again


## Runbook

### Updating Schema or Table Definition

When the dataset structure changes:

1. Update the schema contract: config/schema_expected.yaml
2. Update the PostgreSQL DDL: config/create_table.sql
3. Validate the changes using an updated sample CSV
4. Commit all related changes together

---

### Rerunning the Pipeline with New CSV Drops

To ingest new data:

1. Place the new CSV file under: sample_data/
2. Ensure the CSV schema matches `schema_expected.yaml`
3. Trigger the DAG manually from the Airflow UI

---

### Checklist Before Committing Dataset Changes

Before committing updates to this dataset, ensure:

- [ ] `MANIFEST.md` is updated
- [ ] `schema_expected.yaml` reflects current schema
- [ ] `create_table.sql` is updated if needed
- [ ] Sample CSV is added or updated
- [ ] DAG runs successfully end-to-end
- [ ] No credentials or secrets are committed


