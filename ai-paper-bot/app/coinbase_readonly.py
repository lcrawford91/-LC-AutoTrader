"""Optional authenticated Coinbase Advanced READ-ONLY inspection.

The module deliberately exposes no order creation, cancellation or transfer methods.
Never provide a key with trade or transfer permissions.
"""
from __future__ import annotations
import os

def credential_status() -> dict:
    name = os.getenv("COINBASE_API_KEY_NAME", "")
    private_key = os.getenv("COINBASE_API_PRIVATE_KEY", "")
    return {"configured": bool(name and private_key), "permissions_required": "view only",
            "live_trading_enabled": False, "transfers_enabled": False}

def get_accounts_readonly() -> dict:
    if not credential_status()["configured"]:
        raise RuntimeError("Read-only Coinbase credentials not configured")
    from coinbase.rest import RESTClient
    client = RESTClient(api_key=os.environ["COINBASE_API_KEY_NAME"],
                        api_secret=os.environ["COINBASE_API_PRIVATE_KEY"])
    response = client.get_accounts()
    if hasattr(response, "to_dict"):
        return response.to_dict()
    return dict(response)
