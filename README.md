# Reviews API and CSV Ingestion

## Description

This project is a Reviews API service & a reviews CSV ingestion. The project is a simple ETL pipeline that extracts 
data from a CSV file, transforms the data and loads it into a Postgres database, that is then served through a REST API.

## Setup

1. Clone the repository and enter the project directory
    ```bash
    git clone
    cd reviews-service
    ```

2. Create a virtual environment and install dependencies
    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements-dev.txt
    ```

## Usage

Start the REST API

    ```bash
    fastapi dev src/api/main.py
    ```

You can now access API at: http://127.0.0.1:8000

Run the ETL pipeline

    ```bash
    python src/ingestion/etl.py
    ```


## Testing

Run the tests from main folder

    ```bash
    pytest tests
    ```

## Build image

    ```bash
    direnv allow
    docker build -t tp-api-image --progress=plain .
    docker run -d --name tp-api -p 8000:8000 tp-api-image
    ```

Alternatively, run the entire service

    ```bash
    docker compose build
    docker compose up api db
    ```
   
To ingest the data:

    ```bash
    docker build -t tp-etl-image -f Dockerfile.etl .
    
    direnv allow

    docker run --rm \
      --network tp-network \
      -v /home/stefan/Projects/trustpilot/src/raw_layer/dataops_tp_reviews.csv:/data_in_volume/reviews.csv \
      -e PGHOST=tp-pg \
      -e PGUSER=postgres \
      -e PGPASSWORD=postgres \
      -e PGPORT=5432 \
      -e PGDATABASE=reviews \
      tp-etl-image python src/ingestion/etl.py /data_in_volume/reviews.csv
    ```

## Deploy plan (future work)

- login docker to aws account
- build and tag image
- push image to aws ecr
- deploy image in k8s or ecs
- ideally, automate above steps with CI/CD pipeline
