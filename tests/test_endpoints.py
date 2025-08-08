import pytest
from fastapi.testclient import TestClient
from main import app
from app import database, models, utils

client = TestClient(app)

# Dummy test data
company_data = {
    "name": "Test Logistics",
    "email": "ceo@testlogi.com",
    "password": "ceopass123",
    "address": "123 Street, Chicago"
}

staff_data = {
    "name": "Dispatch One",
    "email": "dispatch@testlogi.com",
    "department": "dispatch"
}

# Register a company
def test_register_company():
    response = client.post("/register", json=company_data)
    assert response.status_code == 200
    assert "company_id" in response.json()

# Login company
def test_login_company():
    response = client.post("/login", data={
        "username": company_data["email"],
        "password": company_data["password"]
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    global ceo_token
    ceo_token = response.json()["access_token"]

# Get company info
def test_get_company_me():
    response = client.get("/company/me", headers={"Authorization": f"Bearer {ceo_token}"})
    assert response.status_code == 200
    assert response.json()["email"] == company_data["email"]

# Invite staff user
def test_invite_staff():
    response = client.post("/invite-user", json=staff_data, headers={"Authorization": f"Bearer {ceo_token}"})
    assert response.status_code == 200
    assert "user_id" in response.json()

# Get staff list
def test_get_company_staff():
    response = client.get("/company/staff", headers={"Authorization": f"Bearer {ceo_token}"})
    assert response.status_code == 200
    assert any(user["department"] == "dispatch" for user in response.json())

# Login staff user
def test_staff_login():
    response = client.post("/staff-login", data={
        "username": staff_data["email"],
        "password": "changeme123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
