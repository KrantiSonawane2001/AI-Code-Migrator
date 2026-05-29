import json
from langchain_core.prompts import ChatPromptTemplate
from .llm_client import get_llm, call_with_retry

llm = get_llm(max_tokens=3000)

prompt = ChatPromptTemplate.from_template("""
You are a senior software engineer specialising in code migration.
Analyse the following legacy code carefully.

Return ONLY a valid JSON object with exactly these fields:
{{
    "summary": "one line description of what this code does",
    "outdated_patterns": ["pattern 1", "pattern 2"],
    "migration_risks": ["risk 1", "risk 2"],
    "complexity": "Low or Medium or High"
}}

No explanation. No markdown. Just the JSON.

Code to analyse:
{code}
""")

def analyse_code(code: str) -> dict:
    chain = prompt | llm
    result = call_with_retry(chain, {"code": code})

    if not result.content.strip():
        return {
            "summary": "Analysis failed",
            "outdated_patterns": [],
            "migration_risks": [],
            "complexity": "Unknown"
        }

    return json.loads(result.content)