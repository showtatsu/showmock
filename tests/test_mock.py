from fastapi.testclient import TestClient
from showmock.server import create_app


app = create_app("./tests/test-data")
client = TestClient(app=app)


def test_get1():
    response = client.get("/v1/sample", headers={'host': 'api.example.com', 'accept': '*/*'})
    assert response.status_code == 200
    assert response.json() == {'sample': 'v1'}


def test_post1():
    response = client.post("/v1/sample", headers={'host': 'api.example.com', 'accept': '*/*'})
    assert response.status_code == 200
    assert response.json() == {'sample': 'v1'}


def test_get2():
    response = client.get("/v1/../../../../v1/sample", headers={'host': 'api.example.com', 'accept': '*/*'})
    assert response.status_code == 200
    assert response.json() == {'sample': 'v1'}


def test_inst():
    from showmock.mockdomain import MockDomain
    m = MockDomain.create_empty_mock()
    assert "v1/sample" == m.normalize_path("/v1/../../../../v1/sample")
