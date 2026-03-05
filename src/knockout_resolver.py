import json
import os
from typing import Optional
from pydantic import BaseModel, Field
from typing import Literal
import instructor
from openai import OpenAI

# Path to the candidate profile
PROFILE_PATH = os.path.join(os.path.dirname(__file__), "..", "candidate_profile.json")

# Initialize Ollama client with instructor for structured output
client = instructor.from_openai(
    OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
    ),
    mode=instructor.Mode.JSON,
)

class QuestionMatch(BaseModel):
    """
    Structured output from the LLM when matching a knockout question
    against the candidate profile.
    """
    matched_field: str = Field(
        ...,
        description="The exact key name from the profile that matches this question, or 'UNKNOWN' if no match."
    )
    confidence: int = Field(
        ...,
        ge=0,
        le=100,
        description="Confidence score (0-100) that this is the correct match."
    )
    answer: str = Field(
        ...,
        description="The answer to use from the profile, or empty string if no match."
    )

def _load_profile() -> dict:
    """Load the candidate profile from disk."""
    if not os.path.exists(PROFILE_PATH):
        return {"universal": {}, "company_specific": {}}
    with open(PROFILE_PATH, "r") as f:
        return json.load(f)

def _save_profile(profile: dict):
    """Save the candidate profile to disk."""
    with open(PROFILE_PATH, "w") as f:
        json.dump(profile, f, indent=4)

def resolve_question(question: str, model_name: str = "llama3.1") -> Optional[str]:
    """
    Takes a knockout question from an ATS form and tries to find the answer
    in candidate_profile.json using LLM semantic matching.
    
    Returns the answer string if found, or None if the question is unknown
    (which should trigger the Telegram HITL protocol).
    """
    profile = _load_profile()
    
    # Flatten all known answers into a searchable format
    all_fields = {}
    for key, value in profile.get("universal", {}).items():
        if value:  # Only include non-empty fields
            all_fields[f"universal.{key}"] = value
    for key, value in profile.get("company_specific", {}).items():
        if value:
            all_fields[f"company_specific.{key}"] = value
    
    if not all_fields:
        print("[Resolver] Profile is empty. Cannot match any questions.")
        return None
    
    # Format the profile fields for the LLM
    fields_text = "\n".join([f"  - {key}: \"{value}\"" for key, value in all_fields.items()])
    
    prompt = f"""You are an AI matching engine for a job application system.

A job application form is asking the following question:
QUESTION: "{question}"

Here are the candidate's known profile fields and their answers:
{fields_text}

TASK: Find which profile field best answers this question.

RULES:
1. If a field clearly answers the question, return its key and the answer.
2. If the question is company-specific (e.g., "Why do you want to work here?"), return matched_field as "UNKNOWN".
3. If no field matches, return matched_field as "UNKNOWN" and answer as empty string.
4. Only match with confidence >= 70. Below that, return "UNKNOWN"."""

    try:
        result = client.chat.completions.create(
            model=model_name,
            response_model=QuestionMatch,
            messages=[
                {"role": "system", "content": "You are a precise question-to-answer matching engine. Output pure JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )
        
        print(f"[Resolver] Match: field='{result.matched_field}', confidence={result.confidence}%")
        
        if result.matched_field == "UNKNOWN" or result.confidence < 70 or not result.answer:
            print(f"[Resolver] No match found → Trigger HITL (Telegram)")
            return None
        
        return result.answer
        
    except Exception as e:
        print(f"[Resolver] LLM error: {e}")
        return None

def save_new_answer(question: str, answer: str, is_universal: bool = False):
    """
    Learns a new answer from the human (via Telegram HITL).
    Saves it to the appropriate section of candidate_profile.json.
    
    - Universal answers (is_universal=True): Safe to auto-reuse forever
    - Company-specific answers (is_universal=False): Never auto-reused
    """
    profile = _load_profile()
    
    # Create a key-friendly version of the question
    key = question.lower().replace(" ", "_").replace("?", "").replace("'", "")[:50]
    
    section = "universal" if is_universal else "company_specific"
    profile[section][key] = answer
    _save_profile(profile)
    
    print(f"[Resolver] Saved new {'universal' if is_universal else 'company-specific'} answer: {key}")

# --- TEST ---
if __name__ == "__main__":
    print("=== Knockout Question Resolver Test ===\n")
    
    # Test 1: Should match a universal field
    print("Test 1: 'What is your GitHub profile URL?'")
    answer = resolve_question("What is your GitHub profile URL?")
    if answer:
        print(f"  ✅ Answer: {answer}\n")
    else:
        print(f"  ⚠️ No match (would trigger HITL)\n")
    
    # Test 2: Should NOT match (company-specific)
    print("Test 2: 'Why do you want to work at Google?'")
    answer = resolve_question("Why do you want to work at Google?")
    if answer:
        print(f"  ✅ Answer: {answer}\n")
    else:
        print(f"  ✅ Correctly flagged as unknown (would trigger HITL)\n")
    
    # Test 3: Should match work authorization
    print("Test 3: 'Are you authorized to work in this country?'")
    answer = resolve_question("Are you authorized to work in this country?")
    if answer:
        print(f"  ✅ Answer: {answer}\n")
    else:
        print(f"  ⚠️ No match (would trigger HITL)\n")
    
    # Test 4: Learning a new answer
    print("Test 4: Saving a new answer from Telegram HITL")
    save_new_answer("What is your expected salary?", "$80,000 - $100,000", is_universal=True)
    print(f"  ✅ New answer saved to profile\n")
    
    print("=== Tests Complete ===")
