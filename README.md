# Trustpilot data engineer test

## Description

This project is a solution to the Trustpilot data engineer test. The project is a simple ETL pipeline that extracts 
data from a CSV file, transforms the data and loads it into a Postgres database, that is then served through a REST API.

## Setup

1. Clone the repository and enter the project directory
    ```bash
    git clone
    cd trustpilot-data-engineer-test
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
    pytest
    ```

