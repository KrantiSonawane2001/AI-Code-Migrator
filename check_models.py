import httpx

api_key = "857f0a14facd45ef99b1df485f718aa7"

models = [
    "gpt-5-nano-2025-08-07",
    "gpt-5-mini-2025-08-07",
    "gpt-5-2025-08-07",
    "gpt-5.2-2025-12-11",
]

headers = {
    "Authorization": f"Bearer {api_key}",
    "genaiplatform-farm-subscription-key": api_key,
    "Content-Type": "application/json"
}

body = {
    "messages": [{"role": "user", "content": "Hi"}],
    "max_completion_tokens": 100
}

for model in models:
    url = f"https://aoai-farm.bosch-temp.com/api/openai/deployments/{model}/chat/completions?api-version=2025-04-01-preview"
    try:
        response = httpx.post(url, headers=headers, json=body, timeout=30.0)
        status = response.status_code
        if status == 200:
            print(f"✅ {model} — WORKS")
        elif status == 401:
            print(f"❌ {model} — No access (401)")
        elif status == 404:
            print(f"❌ {model} — Not found (404)")
        else:
            print(f"⚠️  {model} — Status {status}")
    except Exception as e:
        print(f"❌ {model} — Error: {e}")