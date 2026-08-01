def test_health_check(client):
    response = client.get("/ai/health")

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "status": "running",
        "service": "ExploreCeylon AI Service",
        "version": "1.0.0",
    }
