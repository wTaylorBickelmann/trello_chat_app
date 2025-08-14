"""Nightly cron job run by GitHub Actions.

Flow:
1. Fetch user's new inputs via GitHub Issues (label: daily-input)
2. Archive them to `inputs/` and compute/store embeddings
3. Fetch current open Trello cards
4. Build RAG context from most similar past inputs
5. Ask Gemini to propose new tasks
6. Create Trello cards for those tasks
7. Comment/close processed issues with summary
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List

import numpy as np
from dateutil import tz

from github_utils import get_open_daily_inputs, archive_inputs, comment_and_close
from trello_utils import get_open_cards, create_cards
from trello_extra import get_archived_cards
from gemini_utils import embed_text, generate_tasks

EMBED_FILE = Path("inputs/embeddings.jsonl")
NUM_CONTEXT = 5  # number of similar past inputs to include in prompt


def _load_embeddings() -> List[dict]:
    if EMBED_FILE.exists():
        with open(EMBED_FILE, "r", encoding="utf-8") as f:
            return [json.loads(l) for l in f]
    return []


def _save_embedding(text: str, embedding: List[float]) -> None:
    EMBED_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EMBED_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps({"text": text, "embedding": embedding}) + "\n")


def _select_rag_context(latest_input: str) -> str:
    past = _load_embeddings()
    if not past:
        return ""
    latest_emb = np.array(embed_text(latest_input))
    scored = []
    for item in past:
        emb = np.array(item["embedding"])
        sim = float(latest_emb @ emb / (np.linalg.norm(latest_emb) * np.linalg.norm(emb) + 1e-9))
        scored.append((sim, item["text"]))
    # sort by similarity descending
    scored.sort(reverse=True, key=lambda x: x[0])
    top_texts = [t for _s, t in scored[:NUM_CONTEXT]]
    return "\n---\n".join(top_texts)


def main() -> None:
    issues = get_open_daily_inputs()
    if not issues:
        print("No new user inputs. Exiting.")
        return

    # For simplicity concatenate all issue bodies into one user_input
    user_input_combined = "\n\n".join([iss.body for iss in issues])

    # Archive issues bodies & store embeddings
    archive_inputs(issues)
    emb = embed_text(user_input_combined)
    _save_embedding(user_input_combined, emb)

        # Fetch Trello cards (open + archived) and store their embeddings
    cards_open = get_open_cards()
    cards_arch = get_archived_cards()

    for card in cards_open + cards_arch:
        _save_embedding(card["name"], embed_text(card["name"]))

    card_titles = [c["name"] for c in cards_open]  # For duplicate avoidance

    rag_context = _select_rag_context(user_input_combined)

    new_tasks = generate_tasks(card_titles, user_input_combined, rag_context)
    if not new_tasks:
        print("Gemini generated no tasks.")
    else:
        print("Generated tasks:")
        for t in new_tasks:
            print("-", t)
        # Put Gemini-generated tasks into dedicated list
        create_cards(new_tasks, list_name="Gemini Suggestions")

    # Close issues with comment
    for iss in issues:
        comment_and_close(iss, "Processed by nightly script on Trello.")

    # Timestamp for logs (local timezone)
    print("Completed run at", tz.tzlocal())


if __name__ == "__main__":
    main()
