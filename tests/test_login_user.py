import allure
import pytest

from helpers import make_user


@allure.epic("Stellar Burgers API")
@allure.feature("Логин пользователя")
class TestLoginUser:
    @allure.title("Вход существующего пользователя")
    def test_login_existing_user(self, api, registered_user):
        data = registered_user["data"]
        response = api.login({"email": data["email"], "password": data["password"]})

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["user"] == {"email": data["email"], "name": data["name"]}
        assert body["accessToken"].startswith("Bearer ")
        assert len(body["accessToken"]) > len("Bearer ")
        assert isinstance(body["refreshToken"], str) and body["refreshToken"]

    @allure.title("Вход с неверными данными: {invalid_fields}")
    @pytest.mark.parametrize("invalid_fields", ["email", "password", "both"])
    def test_login_with_invalid_credentials(self, api, registered_user, invalid_fields):
        data = registered_user["data"]
        payload = {"email": data["email"], "password": data["password"]}
        invalid = make_user()
        for field in ("email", "password"):
            if invalid_fields in (field, "both"):
                payload[field] = invalid[field]

        response = api.login(payload)

        assert response.status_code == 401
        assert response.json() == {"success": False, "message": "email or password are incorrect"}
