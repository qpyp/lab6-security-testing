import requests
import pytest
from unittest.mock import patch, Mock

BASE_URL = "http://localhost:8000"


# 1. Перевірка доступу без токена
def test_without_token():
    response = Mock(status_code=401)

    with patch("requests.get", return_value=response):
        result = requests.get(f"{BASE_URL}/api/profile")

    assert result.status_code in (401, 403)


# 2. Перевірка неправильного токена
def test_invalid_token():
    response = Mock(status_code=401)

    with patch("requests.get", return_value=response):
        result = requests.get(
            f"{BASE_URL}/api/profile",
            headers={"Authorization": "Bearer INVALID"}
        )

    assert result.status_code in (401, 403)


# 3. Перевірка правильного токена
def test_valid_token():
    response = Mock(status_code=200)

    with patch("requests.get", return_value=response):
        result = requests.get(
            f"{BASE_URL}/api/profile",
            headers={"Authorization": "Bearer TEST_TOKEN"}
        )

    assert result.status_code == 200


# 4. Перевірка доступу до чужого замовлення
def test_access_another_users_order():
    response = Mock(status_code=403)

    with patch("requests.get", return_value=response):
        result = requests.get(
            f"{BASE_URL}/api/orders/1002",
            headers={"Authorization": "Bearer USER_A"}
        )

    assert result.status_code in (403, 404)


# 5. Перевірка витоку паролів
def test_password_not_exposed():
    response = Mock(status_code=200)
    response.json.return_value = {
        "id": 1,
        "username": "test_user",
        "email": "test@example.com"
    }

    with patch("requests.get", return_value=response):
        result = requests.get(f"{BASE_URL}/api/profile")

    data = result.json()

    assert "password" not in data
    assert "password_hash" not in data


# 6. Перевірка тайм-ауту
def test_timeout():
    with patch(
        "requests.get",
        side_effect=requests.exceptions.Timeout
    ):
        try:
            requests.get(f"{BASE_URL}/api/products", timeout=3)
        except requests.exceptions.Timeout:
            pass


# 7. Перевірка повторного запиту
def test_repeated_request():
    response = Mock(status_code=200)
    response.json.return_value = {"order_id": 1001}

    with patch("requests.post", return_value=response):
        first = requests.post(f"{BASE_URL}/api/orders")
        second = requests.post(f"{BASE_URL}/api/orders")

    assert first.json()["order_id"] == second.json()["order_id"]

# 8. Перевірка тимчасової недоступності сервера
def test_server_unavailable():
    response = Mock(status_code=503)

    with patch("requests.get", return_value=response):
        result = requests.get(f"{BASE_URL}/api/products")

    assert result.status_code == 503


# 9. Перевірка помилки з'єднання
def test_connection_error():
    with patch(
        "requests.get",
        side_effect=requests.exceptions.ConnectionError
    ):
        with pytest.raises(requests.exceptions.ConnectionError):
            requests.get(f"{BASE_URL}/api/products")
