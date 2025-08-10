"""Wrapper around Google Gemini model for embedding and task generation."""
from __future__ import annotations

import os
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
    # Send the user prompt
    resp = chat.send_message(full_prompt)
    lines = [l.strip("- ") for l in resp.text.split("\n") if l.strip()]
    # Deduplicate & filter empties
    return list(dict.fromkeys([ln for ln in lines if ln]))
