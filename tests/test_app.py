from io import BytesIO

import pytest
from src.app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_no_file_in_request(client):
    response = client.post("/classify_file")
    assert response.status_code == 400


def test_no_selected_file(client):
    data = {"file": (BytesIO(b""), "")}  # Empty filename
    response = client.post(
        "/classify_file", data=data, content_type="multipart/form-data"
    )
    assert response.status_code == 400


def test_success(client, mocker):
    mocker.patch("src.app._classify_file", return_value="test_class")

    data = {"file": (BytesIO(b"dummy content"), "file.pdf")}
    response = client.post(
        "/classify_file", data=data, content_type="multipart/form-data"
    )
    assert response.status_code == 200
    assert response.get_json() == {"file_class": "test_class"}
