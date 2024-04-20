#Farhan Sadiq
#1001859500

#I have used the Phonebook starter code provided to us to get started for python.
#I have learned about API and authentication through youtube videos.


'''References
1) https://fastapi.tiangolo.com/
2) https://github.com/sumanentc/python-sample-FastAPI-application
3) https://dassum.medium.com/building-rest-apis-using-fastapi-sqlalchemy-uvicorn-8a163ccf3aa1
'''

#Importing all necessary libraries and classes from the FastAPI framework, Pydantic, and other dependencies.
from fastapi import FastAPI, HTTPException, Security, Depends
from pydantic import BaseModel
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import re
import logging

#Initialize FastAPI app. This is the main class for creating the web application.
app = FastAPI()


#Initialize SQLite database engine to connect to a database file name phonebook.db
engine = create_engine("sqlite:///phonebook.db", echo = True)


#Create base class for database models
Base = declarative_base()

# Define PhoneBook model class
class PhoneBook(Base):
    #Name of the table in the database.
    __tablename__ = "phonebook"
    
    #Defines the primary key column, automatically increments.
    id = Column(Integer, primary_key = True)

    #Column to store the full name of a person
    full_name = Column(String)

    #Column to store the phone number
    phone_number = Column(String)

# Create database schema
Base.metadata.create_all(engine)

# Create session class for database operations
Session = sessionmaker(bind = engine)

# Define Pydantic model class for request and response data
class Person(BaseModel):
    #Declare a model field that expects a string of full name
    full_name: str

    #Declare a model field that expects a string of phone number
    phone_number: str

#Define a function to validate full names.
def validate_name(name):
    #regular expression pattern for valid names
    r_p = r"^[A-Za-z',.\s-]{2,50}$"

    #Check if the name matches the pattern
    return re.match(r_p, name) is not None

#Define a function to validate phone numbers
def validate_phone_number(phone_number):
    #Regular expression pattern for valid phone numbers
    r_p = r"^(?:\+?(\d{1,3}))?[-. (]*(\d{2,4})[-. )]*(\d{3,4})[-. ]*(\d{4})(?: *x(\d+))?$"

    # Check if the phone number matches the pattern
    return re.match(r_p, phone_number) is not None

#Setting up logging to record actions performed on the API, storing logs in phonebook_audit.log
logging.basicConfig(filename = "phonebook_audit.log", level = logging.INFO, format = '%(asctime)s - %(levelname)s - %(message)s')

#Define a function to log different actions
def audit_log(action, name = None):
    if name:
        #Log action and name if provided
        logging.info(f"{action} - {name}")
    else:
        #Log action only if name is not provided
        logging.info(action)

# API Key-based authentication
API_KEY = "secret_api_key"

#Function to retrieve and validate the API key provided by the user; raises an HTTP exception if invalid
def get_api_key(api_key: str = Security(APIKeyHeader(name = "access_token"))):
    if api_key != API_KEY:
        #Exception if API key is not valid
        raise HTTPException(status_code = 403, detail = "Failed to validate credentials")

    #Return the API key if valid
    return api_key

#API endpoints (ADD, LIST, DELBYNAME, DELBYNUMBER)
@app.get("/PhoneBook/list")
def list_phonebook(api_key: str = Depends(get_api_key)):
    #Open a new database session
    session = Session()

    #Query all entries in the phonebook
    p = session.query(PhoneBook).all()

    #Close the database session
    session.close()

    #Return the list of phonebook entries
    return p

@app.post("/PhoneBook/add")
def add_person(person: Person, api_key: str = Depends(get_api_key)):
    if not validate_name(person.full_name) or not validate_phone_number(person.phone_number):
        #Exception if data is invalid
        raise HTTPException(status_code = 400, detail = "Invalid input data")
    
    #Open a new database session
    session = Session()

    #Check if person already exists
    existing_person = session.query(PhoneBook).filter_by(phone_number = person.phone_number).first()
    if existing_person:
        #Close the session if person exists
        session.close()

        #Exception for existing person
        raise HTTPException(status_code = 400, detail = "Person already exists")
    
    #Create a new PhoneBook entry
    new_person = PhoneBook(full_name = person.full_name, phone_number = person.phone_number)
    
    #Add the new entry to the session
    session.add(new_person)

    #Commit the transaction to the database
    session.commit()

    #Close the database session
    session.close()

    #Log the addition of the new person
    audit_log("Added", person.full_name)

    #Return the successful message.
    return {"message": "Person added successfully"}

@app.put("/PhoneBook/deleteByName")
def delete_by_name(full_name: str, api_key: str = Depends(get_api_key)):
    #Open a new database session
    session = Session()

    #Query the person by full name
    person = session.query(PhoneBook).filter_by(full_name = full_name).first()
    if not person:
        #Close the session if person not found
        session.close()

        #Exception for person not found
        raise HTTPException(status_code = 404, detail = "Person not found in the database")
    
    #Delete the person from the database
    session.delete(person)

    #Commit the transaction to the database
    session.commit()

    #Close the database session
    session.close()

    #Log the deletion of the person
    audit_log("Deleted", full_name)

    #Print the successful message
    return {"message": "Person deleted successfully"}

@app.put("/PhoneBook/deleteByNumber")
def delete_by_number(phone_number: str, api_key: str = Depends(get_api_key)):
    #Open a new database session
    session = Session()

    #Query the person by phone number
    person = session.query(PhoneBook).filter_by(phone_number = phone_number).first()
    if not person:
        #Close the session if person not found
        session.close()

        #Exception for person not found
        raise HTTPException(status_code = 404, detail = "Person not found in the database")
    
    #Delete the person from the database
    session.delete(person)

    #Commit the transaction to the database
    session.commit()

    #Close the database session
    session.close()

    #Log the deletion of the person
    audit_log("Deleted", phone_number)

    #Return successful message
    return {"message": "Person deleted successfully"}
