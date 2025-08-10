#!/usr/bin/env python3
"""scripts/debug_gemini.py

Quick CLI helper to test Gemini task generation locally, without GitHub/Trello side-effects.

Examples
--------
1. Provide prompt via flag and simulate existing Trello cards:

    python scripts/debug_gemini.py --prompt "Finish project report and practice guitar" --cards "Buy groceries" "Write blog post"

2. Pipe a longer prompt from stdin:

    echo "Finish project report, practice guitar for 30 min" | python scripts/debug_gemini.py --cards "Buy groceries"

Environment
-----------
Requires `GEMINI_API_KEY` to be set (either in environment or `.env`).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

# Ensure env vars from .env are available
load_dotenv()

# Import after env is loaded
from gemini_utils import generate_tasks  # pylint: disable=wrong-import-position


def main() -> None:
    parser = argparse.ArgumentParser(description="Test Gemini task generation locally.")
    parser.add_argument(
        "--prompt",
        help="User input text; if omitted, the script reads the full stdin stream.",
    )
    parser.add_argument(
        "--cards",
        nargs="*",
        default=[],
        help="Titles of current Trello cards (optional).",
    )
    parser.add_argument(
        "--ctx",
        default="",
        help="Optional RAG context string to send along with the prompt.",
    )
    args = parser.parse_args()

    # Get prompt either from flag or stdin
    prompt = args.prompt if args.prompt is not None else sys.stdin.read().strip()
    if not prompt:
        print("Error: no prompt provided. Use --prompt or pipe text via stdin.")
        sys.exit(1)

    tasks = generate_tasks(args.cards, prompt, args.ctx)

    print("\nGemini proposed tasks ({}):".format(len(tasks)))
    for t in tasks:
        print(f"- {t}")


if __name__ == "__main__":
    main()
