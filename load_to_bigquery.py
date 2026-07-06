import os
from google.cloud import bigquery
from google.api_core.exceptions import Conflict

def load_csv_to_bigquery():
    # Ensure GOOGLE_APPLICATION_CREDENTIALS is set in your environment
    # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/your/service-account-file.json"
    
    # Initialize a BigQuery client
    client = bigquery.Client()
    
    # Define dataset and table
    project_id = client.project
    dataset_id = "neoverse_ai"
    table_id = "sales_history"
    
    dataset_ref = f"{project_id}.{dataset_id}"
    table_ref = f"{dataset_ref}.{table_id}"
    
    # Create dataset if it does not exist
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = "US"
    
    try:
        dataset = client.create_dataset(dataset, timeout=30)
        print(f"Created dataset {dataset.project}.{dataset.dataset_id}")
    except Conflict:
        print(f"Dataset {dataset.project}.{dataset.dataset_id} already exists.")
    except Exception as e:
        print(f"Error creating dataset: {e}")
        return

    # Configure the load job
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True, # Automatically infer schema
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE # Overwrite if table exists
    )

    file_path = "data/sales_history.csv"
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    # Load data from the CSV file to BigQuery
    print(f"Loading data from {file_path} into {table_ref}...")
    with open(file_path, "rb") as source_file:
        load_job = client.load_table_from_file(
            source_file, table_ref, job_config=job_config
        )

    # Wait for the job to complete
    load_job.result()

    # Get the table to confirm the row count
    table = client.get_table(table_ref)
    print(f"Successfully loaded {table.num_rows} rows and {len(table.schema)} columns into {table_ref}.")

if __name__ == '__main__':
    load_csv_to_bigquery()
