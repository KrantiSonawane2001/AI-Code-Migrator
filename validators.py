def validate_code_input(code: str) -> dict:
    warnings = []

    if not code or not code.strip():
        return {
            "valid": False,
            "reason": "No code provided. Please paste your code.",
            "warnings": []
        }

    code_chars = set('{}();[]<>:=!&|+-*/.,@#')
    has_code_chars = any(c in code for c in code_chars)

    if not has_code_chars:
        return {
            "valid": False,
            "reason": "Input does not appear to be code. Please paste actual source code.",
            "warnings": []
        }

    lines = code.strip().split('\n')
    non_empty_lines = [l for l in lines if l.strip()]

    if len(non_empty_lines) < 3:
        return {
            "valid": False,
            "reason": "Code too short. Please provide at least 3 lines of code.",
            "warnings": []
        }

    if len(non_empty_lines) > 300:
        return {
            "valid": False,
            "reason": f"Code too long ({len(non_empty_lines)} lines). Maximum is 300 lines.",
            "warnings": []
        }

    if len(non_empty_lines) > 150:
        warnings.append(
            f"Large file ({len(non_empty_lines)} lines) — will be chunked automatically."
        )

    if '<html' in code.lower() or '<!DOCTYPE' in code.lower():
        warnings.append(
            "HTML detected — migration quality may vary."
        )

    return {
        "valid": True,
        "reason": "OK",
        "warnings": warnings
    }