import pandas as pd
import json
from database import engine
from utils import normalize_salary, clean_html, decode_unicode_escape, insert_on_conflict_nothing
import requests


def extractJob(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url, timeout=15)  # Added timeout for safety
        
        # Check if the request was successful (status code 200)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)

        # Save the result to a file
        with open('jobs.json', 'w') as file:
            file.write(response.text)
        print("Data saved to jobs.json")
        return 'jobs.json'

    except Exception as e:
        print(f"An error occurred while saving the file: {e}")


# Path to your JSON file
file_path = "/Users/ohamugochukwu/Documents/Oham-Job-Board/jobs.json"

def jobETL(file_path):

    # Method 1: Using json.load() to read the file and then convert to a DataFrame
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Convert the JSON object to a DataFrame
    df = pd.DataFrame(data['jobs'])

    # Drop the 'age' column
    df.drop(columns=["company_logo_url"], inplace=True)

    # Clean each salary string
    df['salary'] = df['salary'].apply(normalize_salary)

    # Dictionary specifying the old names and new names
    new_column_names = {
        'id': 'Id',
        'url': 'URL',
        'title': 'Title',
        'company_name': 'CompanyName',
        'company_logo': 'CompanyLogo',
        'category': 'Category',
        'tags': 'Tags',
        'job_type': 'JobType',
        'publication_date': 'PublicationDate',
        'candidate_required_location': 'Location',
        'description': 'Description',
        'salary': 'Salary'
    }

    # Rename columns
    df.rename(columns=new_column_names, inplace=True)

    df['Description'] = df['Description'].apply(clean_html).apply(decode_unicode_escape)

    # Write the DataFrame to a PostgreSQL table using the imported engine
    try:
        df.to_sql('Jobs', engine, if_exists='append', index=False, method=insert_on_conflict_nothing, chunksize=1000)
        print("finsihed loading data into the database")
    except Exception as e:
        print("An error occurred:", e)

# Main function to run the ETL function
if __name__ == "__main__":
    # URL of the resource you want to request
    url = "https://remotive.com/api/remote-jobs"  
    extracted_file = extractJob(url)

    if extracted_file:
        jobETL(extracted_file)


