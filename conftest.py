import platform
from pathlib import Path

import allure
import pytest

from api_client import StellarBurgersApi
from helpers import make_user
from urls import BASE_URL


@pytest.fixture
def api():
    client = StellarBurgersApi()
    yield client
    client.close()


@pytest.fixture
def user_data():
    return make_user()


@pytest.fixture
def register_user(api):
    created = []

    def register(payload):
        response = api.register(payload)
        # Запоминаем аккаунт до проверок теста, чтобы удалить его даже при падении.
        if response.status_code == 200:
            body = response.json()
            if body.get("success"):
                created.append((payload.copy(), body.get("accessToken")))
        return response

    yield register

    errors = []
    for payload, token in reversed(created):
        try:
            with allure.step("Удалить созданного тестового пользователя"):
                if not token:
                    login = api.login({key: payload[key] for key in ("email", "password")})
                    token = login.json()["accessToken"]
                response = api.delete_user(token)
                if response.status_code != 202 or response.json().get("success") is not True:
                    errors.append(f"Удаление пользователя: HTTP {response.status_code}")
        except Exception as error:
            errors.append(f"Ошибка очистки: {type(error).__name__}")
    assert not errors, "; ".join(errors)


@pytest.fixture
def registered_user(register_user, user_data):
    with allure.step("Подготовить уникального зарегистрированного пользователя"):
        response = register_user(user_data)
        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["accessToken"].startswith("Bearer ")
        return {"data": user_data, "token": body["accessToken"]}


@pytest.fixture(scope="session")
def ingredient_ids():
    client = StellarBurgersApi()
    try:
        with allure.step("Получить актуальные хеши ингредиентов из каталога"):
            response = client.get_ingredients()
            assert response.status_code == 200
            body = response.json()
            assert body["success"] is True
            ingredients = body["data"]
            # Состав бургера: две половинки булочки и начинка.
            bun = next(item["_id"] for item in ingredients if item["type"] == "bun")
            filling = next(item["_id"] for item in ingredients if item["type"] == "main")
            return [bun, filling, bun]
    finally:
        client.close()


@pytest.fixture(scope="session", autouse=True)
def allure_environment(pytestconfig):
    yield
    results = pytestconfig.getoption("allure_report_dir")
    if results:
        directory = Path(results)
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "environment.properties").write_text(
            f"Base_URL={BASE_URL}\nPython={platform.python_version()}\n"
            f"OS={platform.system()}\n", encoding="utf-8",
        )
