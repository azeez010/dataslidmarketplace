from os import getenv

ENV = getenv("env")

if ENV == "dev" or not ENV:
    PAYSTACK_SECRET = getenv("paystack_test")
else:
    PAYSTACK_SECRET = getenv("paystack_live")