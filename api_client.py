import json

import allure
import requests

from helpers import redact
from urls import BASE_URL, INGREDIENTS, LOGIN, ORDERS, REGISTER, REQUEST_TIMEOUT, USER


class StellarBurgersApi:
    def __init__(self):
        self.session = requests.Session()

    def close(self):
        self.session.close()

    def _request(self, method, path, payload=None, token=None):
        with allure.step(f"{method} {path}"):
            headers = {"Authorization": token} if token else {}
            allure.attach(
                json.dumps(redact({"headers": headers, "body": payload}), ensure_ascii=False),
                "Запрос", allure.attachment_type.JSON,
            )
            response = self.session.request(
                method, f"{BASE_URL}{path}", json=payload, headers=headers, timeout=REQUEST_TIMEOUT,
            )
            try:
                body = redact(response.json())
            except requests.exceptions.JSONDecodeError:
                body = response.text
            allure.attach(
                json.dumps({"status": response.status_code, "body": body}, ensure_ascii=False),
                "Ответ", allure.attachment_type.JSON,
            )
            return response

    def register(self, payload):
        return self._request("POST", REGISTER, payload)

    def login(self, payload):
        return self._request("POST", LOGIN, payload)

    def delete_user(self, token):
        return self._request("DELETE", USER, token=token)

    def get_ingredients(self):
        return self._request("GET", INGREDIENTS)

    def create_order(self, payload, token=None):
        return self._request("POST", ORDERS, payload, token)
