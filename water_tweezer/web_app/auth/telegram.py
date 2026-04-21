import hashlib
import hmac
from urllib.parse import parse_qsl


def parse_init_data(init_data: str) -> dict:
    return dict(parse_qsl(init_data, keep_blank_values=True))


def verify_telegram_init_data(init_data: str, bot_token: str) -> dict:
    data = parse_init_data(init_data)

    received_hash = data.pop("hash", None)
    if not received_hash:
        raise ValueError("Missing hash")

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))

    secret_key = hashlib.sha256(bot_token.encode("utf-8")).digest()

    computed_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        raise ValueError("Invalid Telegram initData signature")

    return data
