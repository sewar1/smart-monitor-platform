import pytest
from dashboard.app import app

@pytest.fixture
def client():
    """Establishes a dynamic application test client context."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# ==============================================================================
# TELEMETRY INGESTION TESTS (SPRINT 2)
# ==============================================================================

def test_receiver_endpoint_rejects_empty_payload(client):
    """
    TDD Constraint: Enforce that the server MUST reject empty payloads with HTTP 400.
    """
    response = client.post('/api/metrics/receiver', json={})
    assert response.status_code == 400
    assert response.get_json()["status"] == "rejected"

def test_receiver_endpoint_accepts_valid_payload(client):
    """
    TDD Constraint: Enforce that valid telemetry from an Agent returns HTTP 201.
    """
    test_payload = {
        "server": "vmware-test-node",
        "cpu": 25.5,
        "ram": 60.0,
        "disk": 15.2
    }
    response = client.post('/api/metrics/receiver', json=test_payload)
    assert response.status_code == 201
    assert response.get_json()["status"] == "synchronized"


# ==============================================================================
# ENTERPRISE SECURITY RING TESTS (SPRINT 3 - TDD)
# ==============================================================================

def test_dashboard_requires_authentication(client):
    """
    TDD Security Ring Constraint: Accessing global system infrastructure health metrics 
    must require a valid authentication profile (HTTP 401 Unauthorized).
    """
    response = client.get('/api/metrics')
    assert response.status_code == 401
    assert "error" in response.get_json()
    assert "Missing cryptographic identity token" in response.get_json()["error"]

def test_login_endpoint_rejects_invalid_credentials(client):
    """
    TDD Security Ring Constraint: Verify that brute-force or faulty credentials
    are strictly rejected by the bcrypt validation core with HTTP 401.
    """
    bad_payload = {
        "username": "admin",
        "password": "wrong_password_123"
    }
    response = client.post('/api/login', json=bad_payload)
    assert response.status_code == 401
    assert "error" in response.get_json()

def test_login_endpoint_accepts_seeded_admin_credentials(client):
    """
    TDD Security Ring Constraint: Verify that high-fidelity matches against 
    the seeded administrative database record return a functional short-lived JWT.
    """
    admin_payload = {
        "username": "admin",
        "password": "admin_secure_2026"  # القيمة الافتراضية التي قمنا بعمل Seeding لها
    }
    response = client.post('/api/login', json=admin_payload)
    
    assert response.status_code == 200
    assert "token" in response.get_json()
    assert response.get_json()["status"] == "authenticated"

