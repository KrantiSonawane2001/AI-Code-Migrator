from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from graph import run_migration_pipeline
from validators import validate_code_input


# Create FastAPI app
app = FastAPI(
    title="Code Migrator AI",
    description="Migrate legacy code to modern versions using AI agents",
    version="1.0.0",
     allow_origins=["*"],
)

# CORS — allows Angular (running on different port) to talk to FastAPI
# Without this Angular requests get blocked by browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",           # local Angular dev
        "https://your-angular-app.vercel.app"  # production (update later)
    ],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ── Request and Response Models ───────────────────────────────────────
# Pydantic models define exactly what data goes in and out
# FastAPI uses these to validate and document automatically

class MigrationRequest(BaseModel):
    code: str           # the code user pastes

class AgentReview(BaseModel):
    score: int
    patterns_fixed: list
    patterns_missed: list
    bugs_introduced: list
    logic_preserved: bool
    overall_feedback: str

class MigrationResponse(BaseModel):
    success: bool
    source_version: str
    target_version: str
    language: str
    original_code: str
    migrated_code: str
    score: int
    review: dict
    chunks_processed: int
    error: str = ""

# ── Routes ────────────────────────────────────────────────────────────

@app.get("/")
def home():
    """Health check — confirms API is running"""
    return {
        "status": "running",
        "message": "Code Migrator AI is ready"
    }

@app.get("/supported-languages")
def supported_languages():
    """Returns list of supported migration paths"""
    return {
        "languages": [
            "Java 7/8 → Java 21",
            "C++03/11 → C++20/23",
            "Python 2 → Python 3",
            "JavaScript ES5 → ES2023",
            "AngularJS 1.x → Angular 17+"
        ]
    }

@app.post("/migrate", response_model=MigrationResponse)
def migrate_code(request: MigrationRequest):
    """
    Main endpoint — takes legacy code, returns migrated code.

    Steps:
    1. Validate input
    2. Run LangGraph pipeline
    3. Return results
    """

    # Step 1 — Validate
    validation = validate_code_input(request.code)
    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail=validation["reason"]
        )

    # Step 2 — Run pipeline
    try:
        result = run_migration_pipeline(request.code)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Migration pipeline failed: {str(e)}"
        )

    # Step 3 — Build response
    language_info = result.get("language_info", {})

    return MigrationResponse(
        success=result["score"] >= 80,
        source_version=language_info.get("source_version", "Unknown"),
        target_version=language_info.get("target_version", "Unknown"),
        language=language_info.get("language", "Unknown"),
        original_code=request.code,
        migrated_code=result.get("final_migrated_code", ""),
        score=result.get("score", 0),
        review=result.get("review", {}),
        chunks_processed=len(result.get("chunks", [])),
        error=result.get("validation_error", "")
    )