import pandas as pd
import numpy as np
import pickle
import json
from database import engine
from utils import normalize_salary, clean_html, decode_unicode_escape, insert_on_conflict_nothing
import requests
from sqlalchemy import func
from database import get_db, Job
from sentence_transformers import SentenceTransformer
encoder = SentenceTransformer("all-mpnet-base-v2")

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

    try:
        # Method 1: Using json.load() to read the file and then convert to a DataFrame
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Convert the JSON object to a DataFrame
        df = pd.DataFrame(data['jobs'])
        print("loaded")

        # Remove all duplicates in place
        # Specify columns to use for duplicate detection
        df.drop_duplicates(subset=['id'], keep=False, inplace=True)


        # Access the database session
        with next(get_db()) as db:
            # Retrieve the latest publication date from the Jobs table
            latestDate = db.query(func.max(Job.PublicationDate)).scalar()
            dateThreshold = pd.to_datetime(latestDate).date()

            # Retrieve all Job IDs in the database and convert them into a flat list of IDs
            existing_job_ids = [job_id[0] for job_id in db.query(Job.Id).all()]
        
        
        df['publication_date'] = pd.to_datetime(df['publication_date']).dt.date
        print(dateThreshold)

        # Drop rows where 'Date' is less than 'date_threshold'
        df = df[df['publication_date'] > dateThreshold]
        print(df.shape)
        # Filter the DataFrame by selecting rows where 'Id' is not in exclude_ids
        df = df[df['id'].isin(existing_job_ids) == False]
        print(df.shape)

        # Drop the 'company_logo_url' column
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
        df.reset_index(drop=True, inplace=True)

        # print(df['Description'][408])
        print("done cleaning")
        df.to_csv('filename.csv', index=False) 

        if not df.empty:
            print(df.shape)
            # df["Description"] = df["Description"].astype(str)
            # print(df['Description'][408])
            # encd = encoder.encode(df['Description'][408])
            # print(len(encd))
           
            newId = df['Id'].to_list()
            print(len(newId))
            newVectors = encoder.encode(df['Description'])

            with open('Backend/jobIndex.pk1', 'rb') as f:
                jobIndex = pickle.load(f)
                finalJobIndex = np.append(jobIndex, newVectors, axis=0)
                print("Job vectors updated")

            with open('Backend/jobId.pk1', 'rb') as f:
                jobId = pickle.load(f)
                finalJobId = np.append(jobId, newId, axis=0)
                print("Job ID updated")
            
            with open("Backend/jobIndex.pk1", "wb") as f:
                pickle.dump(finalJobIndex, f)
                print("Job vectors saved")

            with open("Backend/jobId.pk1", "wb") as f:
                pickle.dump(finalJobId, f)
                print("Job vectors saved")
        else:
            pass

         # Write the DataFrame to an SQL table
        rows_inserted = df.to_sql('Jobs', engine, if_exists='append', index=False)
        print(f"{rows_inserted} rows were loaded into the database.")
        # df.to_sql('Jobs', engine, if_exists='append', index=False, method=insert_on_conflict_nothing, chunksize=1000)

    except Exception as e:
        print("An error occured:", e)

# Main function to run the ETL function
if __name__ == "__main__":
    encoder = SentenceTransformer("all-mpnet-base-v2")
    # URL of the resource you want to request
    url = "https://remotive.com/api/remote-jobs"  
    extracted_file = extractJob(url)

    if extracted_file:
        jobETL(extracted_file)


