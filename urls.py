import os


BASE_URL = os.getenv(
    "STELLAR_BURGERS_URL", "https://stellarburgers.education-services.ru"
).rstrip("/")
REGISTER = "/api/auth/register"
LOGIN = "/api/auth/login"
USER = "/api/auth/user"
INGREDIENTS = "/api/ingredients"
ORDERS = "/api/orders"
REQUEST_TIMEOUT = float(os.getenv("STELLAR_BURGERS_TIMEOUT", "30"))
