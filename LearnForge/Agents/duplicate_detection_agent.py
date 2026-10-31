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

from logger import L
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
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    client = AsyncOpenAI(
        base_url=OLLAMA_BASE_URL,
        api_key="ollama",
    )
else:
    raise ValueError(
        f"Unsupported LLM_PROVIDER '{LLM_PROVIDER}'. Use 'ollama' or 'openrouter'."
    )

INSTRUCTIONS = """
You are a semantic deduplication agent for a technical learning-question
database. Compare a NEW question against EXISTING questions retrieved from
ChromaDB and classify it as one of:

DUPLICATE: an existing question asks essentially the same thing, even if
worded differently.
NEW: no existing question asks the same thing. Related or similar topics
are still NEW.

Rules:
1. Compare meaning and learning intent, not keywords or ChromaDB distance
   alone.
2. Choose DUPLICATE only if both questions would need essentially the same
   answer. Related topics that ask something different are NEW.
3. For DUPLICATE, set matched_id to the best matching candidate ID (never
   invent one) and canonical_question to that existing question's text.
4. For NEW, set matched_id to null and canonical_question to the new question.
5. Keep reason to one short sentence.
6. Return ONLY a valid JSON object, without markdown.

Required JSON format:
{
    "classification": "DUPLICATE",
    "matched_id": "1",
    "canonical_question": "How does HashMap work internally in Java?",
    "reason": "Both questions ask about the same concept."
}
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
    usage = result.context_wrapper.usage
    L.info(
        "LLM token usage [provider=%s, model=%s]: requests=%d, input=%d, output=%d, total=%d | question=%s",
        LLM_PROVIDER,
        MODEL_NAME,
        usage.requests,
        usage.input_tokens,
        usage.output_tokens,
        usage.total_tokens,
        new_question,
    )
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
