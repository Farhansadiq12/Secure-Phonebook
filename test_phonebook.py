#Farhan Sadiq
#1001859500

#This is the file for the automated unit tests.

#Importing the necessary modules and classes for testing
from fastapi.testclient import TestClient
from pytest import fixture
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_api_key, Base  

#Constants for the tests
API_KEY_HEADER = {"access_token": "secret_api_key"}

# Configure a test database and test client using pytest fixtures
@fixture(scope = "module")
def test_app():
    #Setup test database
    #Create a SQLite database engine for testing
    engine = create_engine("sqlite:///./test_phonebook.db")

    #Create all tables defined by Base in the test database
    Base.metadata.create_all(bind = engine)

    #Create a sessionmaker for the test database
    TestSessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
    
    # Dependency override for API key
    app.dependency_overrides[get_api_key] = lambda: API_KEY_HEADER['access_token']

    # Setup Test Client
    #Create a TestClient instance with the FastAPI application
    client = TestClient(app)

    #Yield the test client for use in tests
    yield client
    
    # Tear down test database. Drop all tables defined by Base in the test database.
    Base.metadata.drop_all(bind=engine)

# Example of a test for adding a person with good input
def test_add_person_good_input(test_app):
    response = test_app.post("/PhoneBook/add", json = {"full_name": "Jane Doe", "phone_number": "123456789"}, headers = API_KEY_HEADER)
   
    #Check if the response status code is 200 (OK)
    assert response.status_code == 200

    #Check if the response JSON matches the expected message
    assert response.json() == {"message": "Person added successfully"}

# Example of a test for attempting to add a person with bad input
def test_add_person_bad_input(test_app):
    response = test_app.post("/PhoneBook/add", json = {"full_name": "123", "phone_number": "not_a_phone"}, headers = API_KEY_HEADER)
    
    #Check if the response status code is 400 (Bad Request)
    assert response.status_code == 400
   
    #Check if the error detail matches the expected message
    assert response.json()["detail"] == "Invalid input data"

# Example of a test for listing all entries
def test_list_phonebook(test_app):
    #Send a GET request to list all entries
    response = test_app.get("/PhoneBook/list", headers = API_KEY_HEADER)
    
    #Check if the response status code is 200 (OK)
    assert response.status_code == 200


