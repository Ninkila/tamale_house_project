import os
import uuid
from contextlib import closing

import pytest
import server
from src.auth import register_user
from src.database import create_users_table, get_connection

from dotenv import load_dotenv
load_dotenv()

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")
requires_postgres = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="Set TEST_DATABASE_URL to run PostgreSQL API integration tests.",
)


@pytest.fixture
def test_client(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", TEST_DATABASE_URL)
    create_users_table()
    server.app.config["TESTING"] = True
    server.app.config["SECRET_KEY"] = "test-secret-key-12345"
    with server.app.test_client() as client:
        yield client


@requires_postgres
def test_session_login_and_logout(test_client):
    suffix = uuid.uuid4().hex
    username = f"user_{suffix}"
    email = f"{username}@example.com"
    password = "password123"

    # Register
    reg_res = test_client.post("/api/auth/register", json={
        "username": username,
        "email": email,
        "password": password,
        "role": "tenant",
        "full_name": "Test Tenant",
    })
    assert reg_res.status_code == 201

    # Check /api/auth/me is authenticated
    me_res = test_client.get("/api/auth/me")
    assert me_res.status_code == 200
    assert me_res.get_json()["authenticated"] is True
    assert me_res.get_json()["user"]["username"] == username

    # Logout
    logout_res = test_client.post("/api/auth/logout")
    assert logout_res.status_code == 200

    # /api/auth/me should now be unauthenticated
    me_after = test_client.get("/api/auth/me")
    assert me_after.status_code == 200
    assert me_after.get_json()["authenticated"] is False

    # Log back in
    login_res = test_client.post("/api/auth/login", json={
        "username": username,
        "password": password,
    })
    assert login_res.status_code == 200
    assert login_res.get_json()["username"] == username


@requires_postgres
def test_landlord_property_crud_and_ownership(test_client):
    suffix = uuid.uuid4().hex
    landlord_user = f"landlord_{suffix}"
    landlord_email = f"{landlord_user}@example.com"
    tenant_user = f"tenant_{suffix}"
    tenant_email = f"{tenant_user}@example.com"

    # Register landlord
    test_client.post("/api/auth/register", json={
        "username": landlord_user,
        "email": landlord_email,
        "password": "password123",
        "role": "landlord",
        "full_name": "Tamale Landlord",
    })

    # Add property as landlord
    add_res = test_client.post("/api/landlord/properties", json={
        "neighborhood": "Nyohini",
        "house_type": "2 Bedroom",
        "monthly_rent_ghs": 1500,
        "rooms": 2,
        "bathrooms": 2,
        "furnishing": "Furnished",
        "water": "Available",
        "electricity": "Prepaid",
        "compound": "Yes",
    })
    assert add_res.status_code == 201
    prop_data = add_res.get_json()
    house_id = prop_data["house_id"]
    assert house_id.startswith("TAM-")

    # View landlord's properties
    my_props = test_client.get("/api/landlord/properties")
    assert my_props.status_code == 200
    props_list = my_props.get_json()
    assert any(p["house_id"] == house_id for p in props_list)

    # Update property
    update_res = test_client.put(f"/api/landlord/properties/{house_id}", json={
        "monthly_rent_ghs": 1700,
        "neighborhood": "Nyohini South",
    })
    assert update_res.status_code == 200
    assert update_res.get_json()["property"]["monthly_rent_ghs"] == 1700

    # Toggle status
    status_res = test_client.patch(f"/api/landlord/properties/{house_id}/status", json={"available": False})
    assert status_res.status_code == 200
    assert status_res.get_json()["available"] is False

    # Logout landlord, login as tenant
    test_client.post("/api/auth/logout")
    test_client.post("/api/auth/register", json={
        "username": tenant_user,
        "email": tenant_email,
        "password": "password123",
        "role": "tenant",
    })

    # Tenant should NOT be allowed to add, update or delete landlord properties
    denied_add = test_client.post("/api/landlord/properties", json={"neighborhood": "Dungu", "monthly_rent_ghs": 1000})
    assert denied_add.status_code == 403

    denied_update = test_client.put(f"/api/landlord/properties/{house_id}", json={"monthly_rent_ghs": 500})
    assert denied_update.status_code == 403

    denied_delete = test_client.delete(f"/api/landlord/properties/{house_id}")
    assert denied_delete.status_code == 403

    # Switch back to landlord and delete
    test_client.post("/api/auth/logout")
    test_client.post("/api/auth/login", json={"username": landlord_user, "password": "password123"})
    del_res = test_client.delete(f"/api/landlord/properties/{house_id}")
    assert del_res.status_code == 200


@requires_postgres
def test_enquiries_and_favourites(test_client):
    suffix = uuid.uuid4().hex
    tenant_user = f"ten_{suffix}"
    tenant_email = f"{tenant_user}@example.com"

    # Register tenant
    test_client.post("/api/auth/register", json={
        "username": tenant_user,
        "email": tenant_email,
        "password": "password123",
        "role": "tenant",
        "full_name": "Active Tenant",
    })

    # Get a property from browse
    houses_res = test_client.get("/api/houses")
    assert houses_res.status_code == 200
    houses = houses_res.get_json()
    assert len(houses) > 0
    target_house_id = houses[0]["house_id"]

    # Save to favourites
    fav_res = test_client.post(f"/api/favourites/{target_house_id}")
    assert fav_res.status_code == 200

    # Get favourites
    favs_list = test_client.get("/api/favourites").get_json()
    assert any(h["house_id"] == target_house_id for h in favs_list)

    # Submit enquiry
    enq_res = test_client.post("/api/enquiries", json={
        "property_id": target_house_id,
        "message": "Is this property still available for inspection this weekend?",
    })
    assert enq_res.status_code == 201

    # Check tenant enquiries
    my_enqs = test_client.get("/api/tenant/enquiries").get_json()
    assert any(e["property_id"] == target_house_id for e in my_enqs)

    # Remove favourite
    unfav_res = test_client.delete(f"/api/favourites/{target_house_id}")
    assert unfav_res.status_code == 200
    favs_after = test_client.get("/api/favourites").get_json()
    assert not any(h["house_id"] == target_house_id for h in favs_after)
