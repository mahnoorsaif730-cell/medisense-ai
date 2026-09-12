"""
rag.py — Retrieval module (Owner: Rameen)

CONTRACT (do not change without telling the whole team):
    retrieve_info(query: str) -> {
        "chunks": [str, ...],       # relevant text chunks to feed the LLM
        "sources": [(name, url), ...]  # e.g. [("MedlinePlus", "https://medlineplus.gov/druginformation.html")]
    }

CURRENT STATE: this is a working stub using fuzzy name-matching over the local CSV,
so the rest of the team can build against real output shapes today.

TODO (Rameen):
    1. Replace `_fuzzy_lookup` with real chunking + embeddings + ChromaDB vector search.
    2. Pull richer data from OpenFDA / DailyMed instead of relying only on medicines.csv.
    3. Build the ChromaDB snapshot ONCE (offline) and load it here — never build live.
"""

import csv
import os
from difflib import get_close_matches

CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "medicines.csv")

SOURCES = [
    ("MedlinePlus", "https://medlineplus.gov/druginformation.html"),
    ("DailyMed / FDA", "https://www.dailymed.nlm.nih.gov/dailymed/"),
]


def _load_medicines():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


_MEDICINES = _load_medicines()
_NAMES = [m["medicine_name"] for m in _MEDICINES]


def _fuzzy_lookup(query: str):
    """Very simple name match — placeholder for real vector search."""
    matches = get_close_matches(query.lower(), [n.lower() for n in _NAMES], n=1, cutoff=0.4)
    if not matches:
        return None
    for m in _MEDICINES:
        if m["medicine_name"].lower() == matches[0]:
            return m
    return None


def retrieve_info(query: str) -> dict:
    """
    Main entry point. Given a free-text query (usually a medicine name,
    sometimes a natural-language question), return grounded chunks + sources.

    If nothing matches, return an empty chunks list — the LLM prompt
    (see safety.py SYSTEM_PROMPT) is responsible for turning that into
    a "Record Not Found" response. Do NOT invent a chunk here.
    """
    record = _fuzzy_lookup(query)
    if record is None:
        return {"chunks": [], "sources": []}

    chunk = (
        f"{record['medicine_name']} is a {record['drug_type']}. "
        f"Main use: {record['main_use']}. "
        f"Common forms: {record['common_forms']}. "
        f"Safety note: {record['safety_note']}"
    )
    return {"chunks": [chunk], "sources": SOURCES}


if __name__ == "__main__":
    # quick manual sanity check — run `python rag.py` to test
    for test_query in ["Paracetamol", "ibuprofen", "Zorbaxamine"]:
        print(test_query, "->", retrieve_info(test_query))
