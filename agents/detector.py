import json
import os
from langchain.prompts import ChatPromptTemplate
from .llm_client import get_llm, call_with_retry

# 3000 — nano needs space to think even for simple tasks
llm = get_llm(max_tokens=3000)

prompt = ChatPromptTemplate.from_template("""
You are an expert programmer with deep knowledge of all 
programming languages and their versions.

Analyse the following code carefully.

Return ONLY a valid JSON object with exactly these fields:
{{
    "language": "the programming language name",
    "source_version": "the specific version this code is written in",
    "target_version": "the latest stable version to migrate to",
    "confidence": "High or Medium or Low",
    "reasoning": "one line explaining the key signals you used to detect this"
}}

No explanation. No markdown. Just the JSON.

Code to analyse:
{code}
""")

def detect_language(code: str) -> dict:
    chain = prompt | llm
    result = call_with_retry(chain, {"code": code})

    print(f"[DEBUG detector] length: {len(result.content)}")

    if not result.content.strip():
        return {
            "language": "Unknown",
            "source_version": "Unknown",
            "target_version": "Latest",
            "confidence": "Low",
            "reasoning": "Could not detect — try increasing tokens"
        }

    return json.loads(result.content)