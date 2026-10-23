import secrets
from uuid import uuid4


def make_user():
    identifier = uuid4().hex
    return {
        "email": f"stellar-api-{identifier}@example.com",
        "password": secrets.token_urlsafe(18),
        "name": f"Stellar {identifier[:8]}",
    }


def redact(value):
    """Не сохранять пароли и токены в общедоступных вложениях Allure."""
    hidden_keys = {"password", "accesstoken", "refreshtoken", "authorization"}
    if isinstance(value, dict):
        return {
            key: "<redacted>" if key.lower() in hidden_keys else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value
