# This file handles the database connection
from sqlalchemy import create_engine, Column, Integer, String, Date, ARRAY, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Loading all environment variable
load_dotenv()

# Format for the connection url
#SQLALCHEMY_DATABASE_URL = "postgresql://<username>:<password>@<ip-address/hostname>/<databasename>"
SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL')

# creating an engine: this is how sqlalchemy connects to the database
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# all the models defined to create a table in postgres will  be extending the base class
# every model represents a table in our database
Base = declarative_base()

# Define a table as a class
class Job(Base):
    __tablename__ = 'Jobs'
    Id = Column(Integer, primary_key=True)
    URL = Column(String(1024))
    Title = Column(String(1024))
    CompanyName = Column(String(1024))
    CompanyLogo = Column(String(1024))
    # Category = Column(String(255))
    Category = Column(Text)
    Tags = Column(ARRAY(String(1024)))
    JobType = Column(String(1024))
    PublicationDate = Column(Date)
    Location = Column(String(1024))
    Description = Column(Text)
    Salary = Column(Integer)

# Create all tables
Base.metadata.create_all(engine)

# A session is required to speak to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



def get_db():
    db = SessionLocal() # talks to the database
    try:
        yield db
    finally:
        db.close()
