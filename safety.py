"""
safety.py — Safety, guardrails & interaction checking (Owner: Afsheen)

CONTRACT (do not change without telling the whole team):
    classify_risk(text: str) -> "low" | "moderate" | "emergency"

Also includes (bonus, needed for Tab 4 — Interaction Checker):
    check_interaction(drug_a: str, drug_b: str) -> {
        "interacts": bool,
        "severity": "none" | "mild" | "moderate" | "severe",
        "explanation": str
    }

TODO (Afsheen):
    1. Expand EMERGENCY_KEYWORDS / MODERATE_KEYWORDS based on real red-flag review.
    2. Expand INTERACTIONS with real pairs relevant to the 20-medicine reference set
       (start with Ibuprofen + Aspirin — see note below).
    3. Finalize the exact wording of EMERGENCY_MESSAGE with the team before demo day.
"""

# --- Risk classification -----------------------------------------------

EMERGENCY_KEYWORDS = [
    "overdose", "took too many", "can't breathe", "cannot breathe",
    "unconscious", "passed out", "chest pain", "severe allergic",
    "swelling of face", "swelling of throat", "poisoning",
]

MODERATE_KEYWORDS = [
    "feel sick", "nausea", "dizzy", "rash", "mild reaction",
    "not feeling well", "side effect",
]

EMERGENCY_MESSAGE = (
    "This may be a medical emergency. Please contact emergency services or "
    "Poison Control immediately, or go to the nearest hospital. "
    "This assistant cannot manage emergencies."
)

SYSTEM_PROMPT = """You are a medical information assistant.
You must ONLY answer using the provided Context block.
If the requested drug or query is not explicitly present in the Context,
state exactly: "The requested information is not available in the verified dataset."
DO NOT use internal training knowledge to infer or extrapolate answers."""


def classify_risk(text: str) -> str:
    """
    Classify a user query into low / moderate / emergency risk.
    This is a keyword-based placeholder — fine for the hackathon MVP,
    but every emergency keyword here must be tested (see TC-04).
    """
    lowered = text.lower()

    if any(kw in lowered for kw in EMERGENCY_KEYWORDS):
        return "emergency"
    if any(kw in lowered for kw in MODERATE_KEYWORDS):
        return "moderate"
    return "low"


# --- Interaction checking (Tab 4) ---------------------------------------

# NOTE: Warfarin is NOT in the 20-medicine reference set.
# Use Ibuprofen + Aspirin as the primary interaction demo case instead.
INTERACTIONS = {
    frozenset(["ibuprofen", "aspirin"]): {
        "interacts": True,
        "severity": "moderate",
        "explanation": "Combining Ibuprofen and Aspirin can increase the risk of "
                        "stomach irritation and bleeding. Discuss with a healthcare professional.",
    },
}


def check_interaction(drug_a: str, drug_b: str) -> dict:
    """Look up a known interaction between two drug names."""
    key = frozenset([drug_a.lower(), drug_b.lower()])
    result = INTERACTIONS.get(key)
    if result:
        return result
    return {
        "interacts": False,
        "severity": "none",
        "explanation": "No known interaction found in the verified dataset for this pair.",
    }


if __name__ == "__main__":
    print(classify_risk("I took 20 tablets of Tylenol by mistake"))  # emergency
    print(classify_risk("I feel a bit sick"))                        # moderate
    print(classify_risk("What is Paracetamol used for?"))            # low
    print(check_interaction("Ibuprofen", "Aspirin"))
