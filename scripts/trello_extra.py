"""Additional Trello helper utilities.

Currently only get_archived_cards() is provided separately to avoid editing the existing
`trello_utils.py` in-place. Feel free to merge into that module later.
"""
from __future__ import annotations

import os
from typing import List, Dict

import requests

_BASE_URL = "https://api.trello.com/1"


def _auth_params() -> Dict[str, str]:
    return {
        "key": os.environ["TRELLO_KEY"],
        "token": os.environ["TRELLO_TOKEN"],
    }


def get_archived_cards(board_id: str | None = None) -> List[Dict]:
    """Return all archived (closed) cards for the board."""
    board_id = board_id or os.environ.get("TRELLO_BOARD_ID")
    resp = requests.get(f"{_BASE_URL}/boards/{board_id}/cards/closed", params=_auth_params())
    resp.raise_for_status()
    return resp.json()
