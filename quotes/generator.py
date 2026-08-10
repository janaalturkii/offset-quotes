import json
from decouple import config
from anthropic import Anthropic

client = Anthropic(api_key=config('ANTHROPIC_API_KEY'))

SYSTEM_PROMPT = """You are a quoting assistant for Offset Events, a Jeddah-based brand activation and event company.

Given a client's brief describing their event needs, generate a professional quotation.

Respond with ONLY valid JSON, no other text, in this exact format:
{
  "client_summary": "one sentence summarizing what the client needs",
  "line_items": [
    {"description": "...", "category": "...", "estimated_price": 0000}
  ],
  "notes": "any assumptions you made or things to clarify with the client"
}

Prices should be in Saudi Riyal (SAR), realistic for the Jeddah event market. Categories should be things like: Venue, Lighting, Branding, Catering, Staffing, AV Equipment, Decor, Photography.
Keep line items to 3-7 realistic items based on what the client described."""


def generate_quote(client_brief: str) -> dict:
    """
    Send a client's plain-language brief to Claude and get back
    a structured quote: summary, line items with prices, and notes.
    """
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": client_brief}
        ]
    )

    raw_text = response.content[0].text.strip()

    # Claude sometimes wraps JSON in ```json fences - strip those if present
    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    return json.loads(raw_text)