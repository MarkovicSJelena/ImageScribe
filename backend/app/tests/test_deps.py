from app.api.deps import get_vision_service


def test_get_vision_service_returns_callable():
    assert callable(get_vision_service())
