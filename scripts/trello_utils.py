"""Utility functions for interacting with the Trello API.
Assumes the following environment variables are set:
- TRELLO_KEY
- TRELLO_TOKEN
- TRELLO_BOARD_ID (board we will add cards to)

Only minimal subset of functionality is implemented (get list names, get open cards,
create cards).
"""
from __future__ import annotations

import os
import requests
from typing import List, Dict

_BASE_URL = "https://api.trello.com/1"


def _auth_params() -> Dict[str, str]:
    return {
        "key": os.environ["TRELLO_KEY"],
        "token": os.environ["TRELLO_TOKEN"],
    }


def get_board_lists(board_id: str | None = None) -> List[Dict]:
    """Return lists (columns) for the board."""
    board_id = board_id or os.environ.get("TRELLO_BOARD_ID")
    resp = requests.get(f"{_BASE_URL}/boards/{board_id}/lists", params=_auth_params())
    resp.raise_for_status()
    return resp.json()


def get_open_cards(board_id: str | None = None) -> List[Dict]:
    """Return all open cards on the board."""
    board_id = board_id or os.environ.get("TRELLO_BOARD_ID")
    params = _auth_params() | {"cards": "open"}
    resp = requests.get(f"{_BASE_URL}/boards/{board_id}/cards/open", params=params)
    resp.raise_for_status()
    return resp.json()


def create_cards(card_titles: List[str], list_name: str = "To Do", board_id: str | None = None) -> None:
    """Create cards with the given titles in the specified list."""
    board_id = board_id or os.environ.get("TRELLO_BOARD_ID")
    lists = get_board_lists(board_id)
    list_id = next((l["id"] for l in lists if l["name"].lower() == list_name.lower()), lists[0]["id"])

    for title in card_titles:
        params = _auth_params() | {"idList": list_id, "name": title}
        resp = requests.post(f"{_BASE_URL}/cards", params=params)
        resp.raise_for_status()
