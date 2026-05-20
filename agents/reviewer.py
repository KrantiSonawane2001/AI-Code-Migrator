import json
from langchain.prompts import ChatPromptTemplate
from .llm_client import get_llm, call_with_retry

llm = get_llm(max_tokens=6000)

prompt = ChatPromptTemplate.from_template("""
You are a senior code reviewer specialising in migration quality.

Review the migration and return ONLY a valid JSON:
{{
    "score": 85,
    "patterns_fixed": ["pattern fixed"],
    "patterns_missed": ["pattern missed if any"],
    "bugs_introduced": ["any new bug if any"],
    "logic_preserved": true,
    "overall_feedback": "one paragraph summary"
}}

Scoring:
- Start at 100
- Subtract 15 per pattern NOT fixed
- Subtract 20 per new bug introduced
- Subtract 30 if logic changed

Original code:
{original_code}

Migrated code:
{migrated_code}

Analysis findings:
{analysis}
""")

def review_migration(
    original_code: str,
    migrated_code: str,
    analysis: dict
) -> dict:

    if not migrated_code.strip():
        print("[Agent 3] Cannot review — migrated code is empty")
        return {
            "score": 0,
            "patterns_fixed": [],
            "patterns_missed": ["Migration failed — no code produced"],
            "bugs_introduced": [],
            "logic_preserved": False,
            "overall_feedback": "Review skipped — Agent 2 produced no output"
        }

    analysis_text = json.dumps(analysis, indent=2)
    chain = prompt | llm
    result = call_with_retry(chain, {
        "original_code": original_code,
        "migrated_code": migrated_code,
        "analysis": analysis_text
    })

    if not result.content.strip():
        return {
            "score": 0,
            "patterns_fixed": [],
            "patterns_missed": [],
            "bugs_introduced": [],
            "logic_preserved": False,
            "overall_feedback": "Review failed — increase tokens"
        }

    return json.loads(result.content)