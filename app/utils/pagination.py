import base64
import json


def encode_cursor(last_id: int, sort_value=None) -> str:
    payload = {"id": last_id}
    if sort_value is not None:
        payload["s"] = str(sort_value)
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()


def decode_cursor(cursor: str) -> dict | None:
    try:
        data = json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
        if not isinstance(data, dict) or "id" not in data:
            return None
        return data
    except Exception:
        return None
