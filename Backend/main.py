from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from .database import engine, get_db, Job
from datetime import datetime, timedelta


app = FastAPI()

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
    db: Session = Depends(get_db)):
    """
    Fetch jobs from the database with pagination.
    :param skip: number of records to skip (for pagination)
    :param limit: number of records to return
    :param db: database session
    :return: list of jobs
    """
    query = db.query(Job)
    print(date)

    # Apply date filter
    if date:
        current_time = datetime.now()
        print(current_time)

        if date == "Past 24 hours":
            past_24_hours = current_time - timedelta(hours=24)
            print(past_24_hours)
            query = query.filter(Job.PublicationDate >= past_24_hours)

        elif date == "Past week":
            past_week = current_time - timedelta(weeks=1)
            query = query.filter(Job.PublicationDate >= past_week)

        elif date == "Past month":
            past_month = current_time - timedelta(days=30)
            query = query.filter(Job.PublicationDate >= past_month)

    # Apply filtering based on the query parameters
    if title:
        query = query.filter(Job.Title.ilike(f"%{title}%"))  # Case-insensitive search
    if location:
        query = query.filter(Job.Location.ilike(f"%{location}%"))  # Case-insensitive search

    total_count = query.count()
    print(total_count)

    # print(query)
    jobs = (
        # db.query(Job)
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
        }
    else:
        raise HTTPException(status_code=404, detail="Job not found")

if __name__ == "__main__":
    uvicorn.run(app)