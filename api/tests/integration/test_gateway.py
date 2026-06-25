def test_gateway_create_and_list(client):
    response = client.post("/gateways", json={"name": "gw-test"})

    assert response.status_code == 200

    data = response.json()
    assert "gateway_uid" in data
    assert "hmac_secret" in data


def test_gateway_uid_is_unique(client):
    r1 = client.post("/gateways", json={"name": "gw1"})
    r2 = client.post("/gateways", json={"name": "gw2"})

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["gateway_uid"] != r2.json()["gateway_uid"]


def test_gateway_secret_only_returned_once(client):
    response = client.post("/gateways", json={"name": "gw-test"})

    data = response.json()
    assert "hmac_secret" in data

    gateway_id = data["id"]

    response2 = client.get(f"/gateways/{gateway_id}")
    data2 = response2.json()

    assert "hmac_secret" not in data2


def test_gateway_list(client):
    client.post("/gateways", json={"name": "gw1"})
    client.post("/gateways", json={"name": "gw2"})

    response = client.get("/gateways")

    assert response.status_code == 200
    assert len(response.json()) >= 2
