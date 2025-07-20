import pytest
import requests

BASE_URL = "http://localhost:8080"

@pytest.fixture
def base_url():
    return BASE_URL

# Test for GET /students/{studentId}
def test_search_student_by_id(base_url):
    student_id = 1  # realistic integer id
    url = f"{base_url}/students/{student_id}"
    response = requests.get(url)
    assert response.status_code == 200
    # Response should be a JSON object
    assert isinstance(response.json(), dict)

# Test for GET /students/greaterThanAge/{age}
def test_filter_students_by_age(base_url):
    age = 18  # realistic age
    url = f"{base_url}/students/greaterThanAge/{age}"
    response = requests.get(url)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

# Test for GET /students/fromCity/{cityName}
def test_filter_students_by_city(base_url):
    city_name = "New York"  # realistic city name
    url = f"{base_url}/students/fromCity/{city_name}"
    response = requests.get(url)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

# Test for GET /students/filterByAgeAndCity with header and query parameters
def test_filter_students_by_age_and_city(base_url):
    url = f"{base_url}/students/filterByAgeAndCity"
    headers = {"schoolId": "SCH123"}  # realistic school id
    params = {"age": 20, "cityName": "Los Angeles"}
    response = requests.get(url, headers=headers, params=params)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

# Test for GET /students/all
def test_get_all_students(base_url):
    url = f"{base_url}/students/all"
    response = requests.get(url)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
