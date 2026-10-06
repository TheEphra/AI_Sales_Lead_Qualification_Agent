import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from src.prompts import LEAD_ANALYSIS_PROMPT


load_dotenv("config/.env")

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL_NAME = "openai/gpt-oss-20b"


def get_client():
    """Create a Hugging Face inference client."""

    if not HF_TOKEN:
        raise ValueError(
            "HF_TOKEN is missing. Add your token to config/.env"
        )

    return InferenceClient(
        provider="auto",
        api_key=HF_TOKEN,
    )


def analyze_lead(
    lead,
    score,
    priority,
    recommended_action,
):
    """Generate grounded AI analysis for a qualified lead."""

    client = get_client()

    lead_data = "\n".join(
        f"{key}: {value}"
        for key, value in lead.items()
    )

    prompt = LEAD_ANALYSIS_PROMPT.format(
        lead_data=lead_data,
        score=score,
        priority=priority,
        recommended_action=recommended_action,
    )

    response = client.chat_completion(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        max_tokens=600,
        temperature=0.2,
    )

    if not response.choices:
        raise RuntimeError(
            "Hugging Face returned no choices."
        )

    message = response.choices[0].message

    content = getattr(message, "content", None)

    if isinstance(content, list):
        content = "".join(
            item.get("text", "")
            for item in content
            if isinstance(item, dict)
        )

    if not content or not str(content).strip():
        raise RuntimeError(
            "The Hugging Face model returned an empty response."
        )

    return str(content).strip()