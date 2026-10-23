import allure
import pytest


@pytest.fixture(params=[True, False], ids=["authorized", "anonymous"])
def order_token(request):
    # Для анонимных заказов не регистрируем лишнего пользователя.
    if request.param:
        return request.getfixturevalue("registered_user")["token"]
    return None


@allure.epic("Stellar Burgers API")
@allure.feature("Создание заказа")
class TestCreateOrder:
    @allure.title("Создание заказа с ингредиентами: {composition}")
    @pytest.mark.parametrize("composition", ["one-ingredient", "burger"])
    def test_create_order_with_ingredients(self, api, ingredient_ids, order_token, composition):
        ingredients = ingredient_ids[:1] if composition == "one-ingredient" else ingredient_ids

        response = api.create_order({"ingredients": ingredients}, token=order_token)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert isinstance(body["name"], str) and body["name"]
        assert type(body["order"]["number"]) is int
        assert body["order"]["number"] > 0

    @allure.title("Создание заказа без ингредиентов: {payload}")
    @pytest.mark.parametrize("payload", [{"ingredients": []}, {}], ids=["empty-list", "missing-field"])
    def test_create_order_without_ingredients(self, api, order_token, payload):
        response = api.create_order(payload, token=order_token)

        assert response.status_code == 400
        assert response.json() == {"success": False, "message": "Ingredient ids must be provided"}

    @allure.title("Создание заказа с неверным хешем: {invalid_hash}")
    @pytest.mark.parametrize(
        "invalid_hash", ["invalid-hash", "61c0c5a71d1f82001bdaaa6z"],
        ids=["invalid-length", "non-hex-character"],
    )
    def test_create_order_with_invalid_ingredient_hash(self, api, order_token, invalid_hash):
        response = api.create_order({"ingredients": [invalid_hash]}, token=order_token)

        # Документация обещает HTTP 500, но не фиксирует JSON-тело ошибки.
        assert response.status_code == 500
