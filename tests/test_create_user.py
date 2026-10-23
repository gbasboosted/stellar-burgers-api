import allure
import pytest


@allure.epic("Stellar Burgers API")
@allure.feature("Создание пользователя")
class TestCreateUser:
    @allure.title("Создание уникального пользователя")
    def test_create_unique_user(self, register_user, user_data):
        response = register_user(user_data)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["user"] == {"email": user_data["email"], "name": user_data["name"]}
        assert body["accessToken"].startswith("Bearer ")
        assert len(body["accessToken"]) > len("Bearer ")
        assert isinstance(body["refreshToken"], str) and body["refreshToken"]

    @allure.title("Повторная регистрация существующего пользователя")
    def test_create_existing_user(self, register_user, registered_user):
        response = register_user(registered_user["data"])

        assert response.status_code == 403
        assert response.json() == {"success": False, "message": "User already exists"}

    @allure.title("Регистрация: обязательное поле {field}, вариант {mode}")
    @pytest.mark.parametrize("field", ["email", "password", "name"])
    @pytest.mark.parametrize("mode", ["missing", "empty"])
    def test_create_user_without_required_field(self, register_user, user_data, field, mode):
        payload = user_data.copy()
        if mode == "missing":
            payload.pop(field)
        else:
            payload[field] = ""

        response = register_user(payload)

        assert response.status_code == 403
        assert response.json() == {
            "success": False, "message": "Email, password and name are required fields",
        }
