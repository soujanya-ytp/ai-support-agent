from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_health():
    r=client.get("/api/health"); assert r.status_code==200 and r.json()["status"]=="ok"

def test_domain_endpoint():
    assert client.get("/api/tickets" if "support" in __file__ else "/api/checks").status_code==200
