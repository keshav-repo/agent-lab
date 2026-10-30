import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    Runner,
    set_tracing_disabled,
)

from models import DuplicateCheckResult, DuplicateClassification, NearestLearningItem

set_tracing_disabled(True)

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").strip().lower()

if LLM_PROVIDER == "openrouter":
    MODEL_NAME = os.getenv("OPENROUTER_MODEL", "gpt-luna")
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY must be set when LLM_PROVIDER=openrouter."
        )
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
elif LLM_PROVIDER == "ollama":
    MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2")
    client = AsyncOpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
    )
else:
    raise ValueError(
        f"Unsupported LLM_PROVIDER '{LLM_PROVIDER}'. Use 'ollama' or 'openrouter'."
    )

INSTRUCTIONS = """
You are a semantic deduplication agent for a technical
learning-question database.

Your job is to compare a NEW question against a list of
EXISTING questions retrieved from ChromaDB.

Classify the new question as one of:

DUPLICATE:
An existing question asks essentially the same thing,
even if the wording is different.

NEW:
No existing question asks the same thing.
Related or similar topics still count as NEW.

Rules:
1. Compare the actual meaning and learning intent.
2. Do not rely solely on ChromaDB distance.
3. Do not classify questions as duplicates simply
   because they contain similar keywords.
4. Prefer DUPLICATE only when two questions would
   require essentially the same answer.
5. Related topics that ask a different question must
   be classified as NEW, never DUPLICATE.
6. Select the best matching candidate ID when the
   classification is DUPLICATE.
7. Never invent a candidate ID.
8. Return ONLY a valid JSON object, without markdown.

Required JSON format:
{
    "classification": "DUPLICATE",
    "matched_id": "1",
    "canonical_question": "How does HashMap work internally in Java?",
    "reason": "Both questions ask about the same concept."
}

For NEW questions, matched_id must be null.
For DUPLICATE questions, matched_id must identify
the matching existing question, and use that
existing question as the canonical question.
"""

dedup_agent = Agent(
    name="Learning Deduplication Agent",
    instructions=INSTRUCTIONS,
    model=OpenAIChatCompletionsModel(
        model=MODEL_NAME,
        openai_client=client,
    ),
    output_type=DuplicateCheckResult
)


def check_duplicate(
    new_question: str,
    candidates: list[NearestLearningItem],
) -> DuplicateCheckResult:
    """
    Compare a new question against existing ChromaDB candidates.
    """

    if not candidates:
        return DuplicateCheckResult(
            classification=DuplicateClassification.NEW,
            matched_id=None,
            canonical_question=new_question,
            reason="No existing candidates found.",
        )

    candidate_text = "\n\n".join(
        f"ID: {candidate.id}\n"
        f"Question: {candidate.document}\n"
        f"Distance: {candidate.distance}"
        for candidate in candidates
    )

    prompt = f"""
    NEW QUESTION:
    {new_question}
    
    EXISTING QUESTIONS:
    {candidate_text}
    
    Determine whether the new question is DUPLICATE or NEW.
    """

    result = Runner.run_sync(dedup_agent, prompt)
    return result.final_output

#
# if __name__ == "__main__":
#
#     new_question = "Explain HashMap Internal working?"
#
#     candidates = [
#         NearestLearningItem(
#             id="1",
#             document="How does HashMap work internally in Java?",
#             distance=0.29,
#         ),
#         NearestLearningItem(
#             id="2",
#             document="Explain HashMap implementation",
#             distance=0.31,
#         ),
#         NearestLearningItem(
#             id="3",
#             document="How are collisions handled in HashMap?",
#             distance=0.35,
#         ),
#     ]
#
#     result = check_duplicate(new_question, candidates)
#
#     print(result.model_dump_json(indent=2))
#
