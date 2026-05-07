import os
import json

from openai import OpenAI

SYSTEM_PROMPT = """
You are MarketSim AI, an enterprise marketing analytics strategist.

Responsibilities:
- Explain forecast performance
- Identify business drivers
- Explain forecast variance
- Identify operational risks
- Recommend optimization experiments
- Summarize executive insights

Tone:
- Executive
- Analytical
- Concise
- Enterprise-focused
"""

def ask_analyst(
    question,
    scenario_context,
    metrics,
    drift,
    api_key,
    model=None,
    max_output_tokens=400,
):
    client = OpenAI(api_key=api_key)

    payload = {
        "question": question,
        "scenario_context": scenario_context,
        "model_metrics": metrics,
        "drift_summary": drift,
    }

    api_response = client.responses.create(
        model=model or os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        instructions=SYSTEM_PROMPT,
        input=json.dumps(payload, indent=2),
        max_output_tokens=max_output_tokens,
    )

    # Safely extract text
    try:
        return api_response.output_text

    except Exception:
        try:
            return api_response.output[0].content[0].text
        except Exception as e:
            return f"OpenAI response parsing error: {str(e)}"