import json
from langchain.prompts import ChatPromptTemplate
from .llm_client import get_llm, call_with_retry

llm = get_llm(max_tokens=8000)

prompt = ChatPromptTemplate.from_template("""
You are a senior software engineer specialising in code migration.

Your task:
Migrate the following {source_version} code to {target_version}.

Fix every outdated pattern listed in the analysis below.
Use the most modern, idiomatic style for {target_version}.

Rules:
- Keep the same class name and method signatures
- Keep the same business logic — only modernise HOW it is written
- Fix every single pattern listed in the analysis
- Return ONLY the migrated code — no markdown, no backticks, no explanation

Analysis of what needs fixing:
{analysis}

Code to migrate:
{code}
""")

def migrate_code(code: str, analysis: dict) -> str:
    analysis_text = json.dumps(analysis, indent=2)

    # Get version info from analysis
    # Detector already figured this out — we just pass it through
    source = analysis.get("source_version", "legacy version")
    target = analysis.get("target_version", "latest stable version")

    chain = prompt | llm
    result = call_with_retry(chain,{
        "code": code,
        "analysis": analysis_text,
        "source_version": source,
        "target_version": target
    })

    print(f"[DEBUG migrator] length: {len(result.content)}")
    return result.content