def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_styles_endpoint(client):
    response = client.get("/api/styles")
    assert response.status_code == 200
    assert response.json() == [
        "Standard",
        "Short",
        "Detailed",
        "SEO / E-commerce",
        "Creative",
    ]
