import httpx
import os
import time
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def get_llm(max_tokens: int = 2000):
    custom_client = httpx.Client(
        headers={
            "Authorization": f"Bearer {os.getenv('BOSCH_API_KEY')}",
            "genaiplatform-farm-subscription-key": os.getenv("BOSCH_API_KEY")
        },
        timeout=120.0  # increased to 2 mins — nano thinks slowly
    )

    llm = AzureChatOpenAI(
        azure_deployment=os.getenv("DEPLOYMENT_NAME"),
        azure_endpoint=os.getenv("BOSCH_ENDPOINT"),
        api_key="placeholder",
        api_version=os.getenv("AZURE_API_VERSION"),
        http_client=custom_client,
        temperature=1,
        model_kwargs={
            "max_completion_tokens": max_tokens
        }
    )
    return llm
def call_with_retry(chain, inputs: dict, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return chain.invoke(inputs)

        except Exception as e:
            error_type = type(e).__name__
            is_last_attempt = attempt == max_retries - 1

            if is_last_attempt:
                print(f"[LLM] Failed after {max_retries} attempts: {error_type}")
                raise

            wait_seconds = 5 * (2 ** attempt)
            print(f"[LLM] {error_type} — retrying in {wait_seconds}s "
                  f"(attempt {attempt + 1}/{max_retries})")
            time.sleep(wait_seconds)

    return None