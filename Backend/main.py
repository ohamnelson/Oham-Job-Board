from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from Backend.database import engine, get_db, Job
from datetime import datetime, timedelta
from sentence_transformers import SentenceTransformer
import numpy as np
import pickle
import faiss
from Backend.utils import compute_cosine_similarities, get_n_max_indices, get_values_from_indices


app = FastAPI()
encoder = SentenceTransformer("all-mpnet-base-v2")

# Add CORS middleware
origins = [
    "http://127.0.0.1:5500",  # Allow your front-end application
    "http://localhost:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows requests from specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

@app.get("/jobs")
def fetch_jobs(
    offset: int = 0, 
    limit: int = 10, 
    title: Optional[str] = Query(None),  # Optional filter for title
    location: Optional[str] = Query(None),  # Optional filter for location
    date: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    db: Session = Depends(get_db)):
    """
    Fetch jobs from the database with pagination.
    :param skip: number of records to skip (for pagination)
    :param limit: number of records to return
    :param db: database session
    :return: list of jobs
    """
    query = db.query(Job)
    print(sort)

    # Apply date filter
    if date:
        current_time = datetime.now()
        print(current_time)

        if date == "Past 24 hours":
            past_24_hours = current_time - timedelta(hours=24)
            print(past_24_hours)
            query = query.filter(Job.PublicationDate >= past_24_hours.date())

        elif date == "Past week":
            past_week = current_time - timedelta(weeks=1)
            query = query.filter(Job.PublicationDate >= past_week.date())

        elif date == "Past month":
            past_month = current_time - timedelta(days=30)
            query = query.filter(Job.PublicationDate >= past_month.date())
        
        elif date == "Any time":
            pass

    # Apply filtering based on the query parameters
    if title:
        query = query.filter(Job.Title.ilike(f"%{title}%"))  # Case-insensitive search
    if location:
        query = query.filter(Job.Location.ilike(f"%{location}%"))  # Case-insensitive search

    # Apply sort filter
    if sort == "date":
        print(sort == "date")
        query = query.order_by(Job.PublicationDate.desc())


    total_count = query.count()
    print(total_count)

    jobs = (
        query
        # .order_by(Job.PublicationDate.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return {
        "jobCount": total_count,
        "jobs": jobs
    }

@app.get("/job/{jobId}")
async def get_job(jobId: int, db: Session = Depends(get_db)):

    # Query the database to get the job with the given job_id
    job = db.query(Job).filter(Job.Id == jobId).first()

    if job:
        return {
            "Title": job.Title,
            "Description": job.Description,
            "CompanyLogo": job.CompanyLogo,
            "CompanyName": job.CompanyName,
        }
    else:
        raise HTTPException(status_code=404, detail="Job not found")
    
@app.get("/job/similar/{jobId}")
async def get_job(jobId: int, db: Session = Depends(get_db)):

    # Query the database to get the job with the given job_id
    job = db.query(Job).filter(Job.Id == jobId).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    try:
        # Encode the job description
        searchQuery = encoder.encode(job.Description)
        searchQuery = searchQuery.reshape((1, -1))  # Ensure vector has shape (1, 768)
        print(f"Search query shape: {searchQuery.shape}")

        # Load the FAISS index and job IDs from disk
        with open('Backend/jobIndex.pk1', 'rb') as jobIndexFile, \
             open('Backend/jobId.pk1', 'rb') as jobIdFile:
            jobIndex = pickle.load(jobIndexFile)
            print(jobIndex.shape)
            jobId = pickle.load(jobIdFile)
            print(len(jobId))
            print("Job vectors and IDs loaded")

        final = compute_cosine_similarities(jobIndex, searchQuery)
        position = get_n_max_indices(final, 11)
        jobPosition = get_values_from_indices(jobId, position)
        print(jobPosition)
        
        # Query the database to get the matching jobs
        results = db.query(Job).filter(Job.Id.in_(jobPosition)).all()

        # Create a dictionary with Ids as keys for easy lookup
        job_dict = {job.Id: job for job in results}

        # Sort results according to the order in jobPosition
        sorted_results = [job_dict[job_id] for job_id in jobPosition if job_id in job_dict]

        # Return job IDs and results exept the 1st index; which is the same as the search query
        return {
            "results": sorted_results,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

    finally:
        # Resources like file handles and db session will automatically be cleaned up here
        print("Cleanup complete")


if __name__ == "__main__":
    uvicorn.run(app)