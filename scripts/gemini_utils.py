"""Wrapper around Google Gemini model for embedding and task generation."""
from __future__ import annotations

import os
import logging
from dotenv import load_dotenv

# Load variables from a .env file in project root, if present
load_dotenv()
from typing import List

import google.generativeai as genai

_GENAI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not _GENAI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY env var not set.")

genai.configure(api_key=_GENAI_API_KEY)

EMBED_MODEL = genai.embed_content
CHAT_MODEL = genai.GenerativeModel("gemini-2.5-pro")

# Generic system prompt sent to Gemini each time. Modify as desired.
SYSTEM_PROMPT = (
    "You are an assistant that helps break down the user's planned activities into actionable Trello cards. "
    "Use the user's latest input along with past inputs to create concise, clear tasks suitable for the next day. "
    "Avoid duplicates with existing cards. Respond with one task per line."
    "Use context to create tasks that are relevant to the user's goals."
    "Creates tasks in appropriate list that are suggested based on what you know about the user's goals."
    "Add tasks to typical executions will be at 1am so tasks taken from user's input should be added to 'Today's list' unless otherwise specified"
    "Based on context or past input tasks can be suggested and added to 'Gemini suggestions' list.\n\nReturn the tasks as a JSON array, each object having:\n- title: string\n- priority: \"primary\" or \"secondary\"\n- subtasks: array of strings (can be empty).\nDo NOT wrap the JSON in markdown fencing or any additional text."
)

def embed_text(text: str) -> List[float]:
    """Return embedding vector for the text."""
    return EMBED_MODEL(model="models/embedding-001", content=text)["embedding"]


def generate_tasks(current_cards: List[str], user_input: str, rag_context: str) -> List[str]:
    """Ask Gemini to propose tasks for the next day.

    Args:
        current_cards: Names of tasks currently on the Trello board.
        user_input: Raw text input from the user for next day.
        rag_context: Concatenated historical inputs to provide context.
    Returns:
        List of new task strings.
    """
    full_prompt = (
        f"Current open Trello cards:\n{chr(10).join(current_cards)}\n\n"
        f"User's latest input for tomorrow:\n{user_input}\n\n"
        f"Relevant past context:\n{rag_context}\n\n"
        "---\nGenerate new tasks:" 
    )
        # Start chat with the system prompt provided as a first user message (Gemini SDK only allows 'user'/'model' roles)
    chat = CHAT_MODEL.start_chat(history=[{"role": "user", "parts": [SYSTEM_PROMPT]}])
    # Send the user prompt and attempt to extract text
    resp = chat.send_message(full_prompt)
    try:
        raw_text = resp.text
    except ValueError:
        # Gemini returned no textual content (e.g., blocked or empty). Bail gracefully.
        logging.warning("Gemini response contained no text. finish_reason=%s. Safety info=%s", getattr(resp.candidates[0], "finish_reason", "unknown"), getattr(resp.candidates[0], "safety_ratings", "n/a"))
        return []

    import json

    # Try JSON first
    try:
        task_objs = json.loads(raw_text)
        if isinstance(task_objs, list) and all(isinstance(t, dict) for t in task_objs):
            return task_objs  # already structured
    except Exception:  # noqa: BLE001
        pass

    # Fallback to plain lines
    lines = [l.strip("- ") for l in raw_text.split("\n") if l.strip()]
    if not lines:
        logging.warning("Gemini returned empty task list after parsing. finish_reason=%s. Safety info=%s", getattr(resp.candidates[0], 'finish_reason', 'unknown'), getattr(resp.candidates[0], 'safety_ratings', 'n/a'))
        return []

    return [{"title": ln, "priority": "secondary", "subtasks": []} for ln in dict.fromkeys(lines)]
