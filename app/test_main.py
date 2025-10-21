"""
 MIT License
 
 Copyright (c) 2024 Riccardo Leonelli
 
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 
 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.
 
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
 
"""

from datetime import date, datetime, timedelta
from fastapi import Depends, HTTPException, Request, status
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch, mock_open
from jose import JWTError, jwt

from app.dependencies import TokenData, cookie_extractor, create_access_token, get_current_employee, get_current_manager
from app.main import app
from app.repo.AccessRepository import AccessRepository
from app.services.AccessService import AccessService
from app.utility.DateUtility import DateUtility

client = TestClient(app)
class MockSettings:
    SECRET_KEY_JWT = "testsecretkey"
    ALGORITHM_JWT = "HS256"
def get_settings():
    return MockSettings()
app.dependency_overrides[get_settings] = get_settings

def get_settings():
    return MockSettings()

@pytest.fixture
def access_service():
    service = AccessService()
    service.repository = MagicMock(spec=AccessRepository)
    return service



# AccessService Tests
def test_get_access_by_date(access_service):
    access_service.repository.get_access_by_date.return_value = [{"date": "2024-05-21"}]
    result = access_service.get_access_by_date("2024-05-21")
    assert result == [{"date": "2024-05-21"}]
    access_service.repository.get_access_by_date.assert_called_once_with("2024-05-21")

def test_get_registry(access_service):
    access_service.repository.get_registry.return_value = [{"employee_id": "123456", "name": "John Doe"}]
    result = access_service.get_registry()
    assert result == [{"employee_id": "123456", "name": "John Doe"}]
    access_service.repository.get_registry.assert_called_once()

def test_person_exists(access_service):
    access_service.repository.person_exists.return_value = True
    result = access_service.person_exists(123456)
    assert result is True
    access_service.repository.person_exists.assert_called_once_with(123456)

def test_add_person(access_service):
    access_service.add_person(123456, "John", "Doe", "john.doe@example.com", "Developer", "2023-01-01", "2023-12-31", "password123")
    access_service.repository.add_person.assert_called_once_with(
        123456, "John", "Doe", "john.doe@example.com", "Developer", "2023-01-01", "2023-12-31", "password123"
    )

def test_update_person(access_service):
    access_service.update_person(123456, "John", "Doe", "john.doe@example.com", "Developer", "2023-01-01", "2023-12-31", "password123")
    access_service.repository.update_person.assert_called_once_with(
        123456, "John", "Doe", "john.doe@example.com", "Developer", "2023-01-01", "2023-12-31", "password123"
    )

def test_delete_person(access_service):
    access_service.delete_person(123456)
    access_service.repository.delete_person.assert_called_once_with(123456)

def test_insert_access(access_service):
    access_service.insert_access(123456)
    access_service.repository.insert_access.assert_called_once_with(123456)

def test_insert_access_manual(access_service):
    timestamp = "2024-05-21T15:30:00"
    creator = "admin"
    access_service.insert_access_manual(123456, timestamp, creator)
    access_service.repository.insert_access_manual.assert_called_once_with(123456, timestamp, creator)

@patch('pandas.DataFrame.to_excel')
def test_extract_delays(mock_to_excel, access_service):
    access_service.repository.extract_delays.return_value = [
        {"employee_id": 123, "delay_minutes": Decimal('15.0')}
    ]
    result = access_service.extract_delays("2024-05-21")
    assert result == "delays_05212024.xlsx"
    mock_to_excel.assert_called_once()

@patch('pandas.DataFrame.to_excel')
def test_create_excel_report(mock_to_excel, access_service):
    access_service.repository.get_report_data.return_value = [
        {"employee_id": 123, "access_time": "2024-05-21T08:00:00"},
        {"employee_id": 123, "access_time": "2024-05-21T16:00:00"}
    ]
    access_service


# DateUtility Tests
def test_format_time_with_invalid_type():
    d = date(2024, 5, 21)
    assert DateUtility.format_time(d) == '00:00'

def test_format_date_with_datetime():
    dt = datetime(2024, 5, 21, 15, 30)
    assert DateUtility.format_date(dt) == '21-05-2024'

# API Endpoint Tests
def test_add_or_update_person():
    response = client.post("/api/add_or_update_person", data={
        "rowId": 123456789,
        "first_name": "MOCK_NAME",
        "last_name": "MOCK_SURNAME",
        "email": "MOCK.MAIL@example.com",
        "role": "IT",
        "hire_date": "2023-01-01",
        "end_date": "2023-12-31",
        "user_password": "password123"
    })
    assert response.status_code == 200
    assert response.json() in [{"message": "Person updated"}, {"message": "Person added"}]

def test_insert_presence():
    response = client.post("/api/insert_presence", data={"id": "123456789"})
    assert response.status_code == 200
    assert response.json() == {"message": "Presence logged successfully"}

def test_delete_person():
    response = client.post("/api/delete_person", data={"rowId": 123456789})
    assert response.status_code == 200
    assert response.json() == {"message": "Person deleted"}

@patch('app.services.AccessService.AccessService.extract_delays')
def test_extract_delays(mock_extract_delays):
    mock_extract_delays.return_value = 'delays_05012024.xlsx'
    with patch('os.path.exists', return_value=True), \
         patch('builtins.open', mock_open(read_data="data")) as mocked_file:
        response = client.get("/api/extract_delays", params={"monthYear": "2023-05-01"})
        assert response.status_code == 200
        mocked_file.assert_called_with('delays_05012024.xlsx', 'rb')

@patch('app.services.AccessService.AccessService.create_excel_report', return_value='month_report_2024_05.xlsx')
@patch('os.path.exists', return_value=True)
@patch('builtins.open', new_callable=MagicMock)
def test_create_excel_report(mock_open, mock_exists, mock_create_excel_report):
    response = client.get("/api/create_excel_report", params={"monthYear": "2024-05-01"})
    assert response.status_code == 200
    assert response.headers['content-type'] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
# Token and Cookie Tests
def test_cookie_extractor():
    mock_request = MagicMock()
    mock_request.cookies.get.return_value = "mock_token"
    token = cookie_extractor(mock_request)
    assert token == "mock_token"
    mock_request.cookies.get.assert_called_once_with("access_token")

def test_cookie_extractor_no_token():
    mock_request = MagicMock()
    mock_request.cookies.get.return_value = None
    with pytest.raises(HTTPException) as excinfo:
        cookie_extractor(mock_request)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Authentication token not found"

@patch('jose.jwt.decode')
def test_get_current_manager(mock_jwt_decode):
    mock_jwt_decode.return_value = {"email": "manager@example.com", "role": "CEO"}
    token = "mock_token"
    token_data = get_current_manager(token)
    assert token_data.username == "manager@example.com"
    assert token_data.role == "CEO"

@patch('jose.jwt.decode')
def test_get_current_manager_invalid_role(mock_jwt_decode):
    mock_jwt_decode.return_value = {"email": "manager@example.com", "role": "Employee"}
    token = "mock_token"
    with pytest.raises(HTTPException) as excinfo:
        get_current_manager(token)
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
    assert excinfo.value.detail == "Invalid authentication credentials"

@patch('jose.jwt.decode', side_effect=JWTError)
def test_get_current_manager_jwt_error(mock_jwt_decode):
    token = "mock_token"
    with pytest.raises(HTTPException) as excinfo:
        get_current_manager(token)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Invalid authentication credentials"

@patch('jose.jwt.decode')
def test_get_current_employee(mock_jwt_decode):
    mock_jwt_decode.return_value = {"email": "employee@example.com", "role": "Employee"}
    token = "mock_token"
    token_data = get_current_employee(token)
    assert token_data.username == "employee@example.com"
    assert token_data.role == "Employee"

@patch('jose.jwt.decode', side_effect=JWTError)
def test_get_current_employee_jwt_error(mock_jwt_decode):
    token = "mock_token"
    with pytest.raises(HTTPException) as excinfo:
        get_current_employee(token)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Invalid authentication credentials"
