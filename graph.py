from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from agents.detector import detect_language
from agents.chunker import chunk_code, reassemble_chunks
from agents.analyser import analyse_code
from agents.migrator import migrate_code
from agents.reviewer import review_migration
from validators import validate_code_input

# ── State ─────────────────────────────────────────────────────────────
class MigrationState(TypedDict):
    original_code: str
    language_info: dict
    chunks: list
    current_chunk_index: int
    migrated_chunks: list
    analysis: dict
    migrated_code: str
    review: dict
    score: int
    retry_count: int
    final_migrated_code: str
    all_reviews: list
    best_migrated_code: str
    best_score: int
    validation_error: str    # ← add this

# ── Node: Detect Language ─────────────────────────────────────────────
def run_detector(state: MigrationState) -> dict:
    print("\nDetector: Identifying language...")
    language_info = detect_language(state["original_code"])
    print(f"Detected: {language_info['source_version']} → {language_info['target_version']}")
    return {"language_info": language_info}

# ── Node: Chunk Code ──────────────────────────────────────────────────
def run_chunker(state: MigrationState) -> dict:
    language = state["language_info"].get("language", "Unknown")
    chunks = chunk_code(state["original_code"], language)
    total = len(chunks)
    if total > 1:
        print(f"\nChunker: Split into {total} chunks")
    else:
        print(f"\nChunker: No splitting needed")
    return {
        "chunks": chunks,
        "current_chunk_index": 0,
        "migrated_chunks": [],
        "all_reviews": []
    }

# ── Node: Analyse Current Chunk ───────────────────────────────────────
def run_analyser(state: MigrationState) -> dict:
    idx = state["current_chunk_index"]
    chunk = state["chunks"][idx]
    total = len(state["chunks"])
    print(f"\nAgent 1: Analysing chunk {idx + 1}/{total}...")

    analysis = analyse_code(chunk["code"])

    # Inject language info into analysis
    # So migrator knows exactly what version to target
    analysis["source_version"] = state["language_info"].get("source_version", "legacy")
    analysis["target_version"] = state["language_info"].get("target_version", "latest")
    analysis["language"] = state["language_info"].get("language", "Unknown")

    print(f"Complexity: {analysis.get('complexity', 'Unknown')}")
    return {"analysis": analysis, "retry_count": 0}

# ── Node: Migrate Current Chunk ───────────────────────────────────────
def run_migrator(state: MigrationState) -> dict:
    idx = state["current_chunk_index"]
    total = len(state["chunks"])
    retry = state["retry_count"]
    chunk = state["chunks"][idx]

    # Add language info to analysis for targeted migration
    analysis = state["analysis"].copy()
    analysis["target_version"] = state["language_info"].get("target_version", "latest")

    if retry == 0:
        print(f"\nAgent 2: Migrating chunk {idx + 1}/{total}...")
    else:
        print(f"\nAgent 2: Retry {retry} for chunk {idx + 1}/{total}...")

    migrated = migrate_code(chunk["code"], analysis)
    return {"migrated_code": migrated}

# ── Node: Review Current Chunk ────────────────────────────────────────
def run_reviewer(state: MigrationState) -> dict:
    idx = state["current_chunk_index"]
    total = len(state["chunks"])
    print(f"\nAgent 3: Reviewing chunk {idx + 1}/{total}...")

    review = review_migration(
        state["chunks"][idx]["code"],
        state["migrated_code"],
        state["analysis"]
    )
    score = review.get("score", 0)
    print(f"Score: {score}/100")
    return {"review": review, "score": score}

# ── Node: Save Chunk Result ───────────────────────────────────────────
def save_chunk_result(state: MigrationState) -> dict:
    # Save migrated chunk and its review
    migrated_chunks = list(state["migrated_chunks"])
    all_reviews = list(state["all_reviews"])

    migrated_chunks.append(state["migrated_code"])
    all_reviews.append(state["review"])

    # Move to next chunk
    next_index = state["current_chunk_index"] + 1

    return {
        "migrated_chunks": migrated_chunks,
        "all_reviews": all_reviews,
        "current_chunk_index": next_index,
        "retry_count": 0
    }

# ── Node: Reassemble All Chunks ───────────────────────────────────────
def run_reassembler(state: MigrationState) -> dict:
    print("\nReassembling chunks into final file...")
    final_code = reassemble_chunks(state["migrated_chunks"])

    # Calculate average score across all chunks
    scores = [r.get("score", 0) for r in state["all_reviews"]]
    avg_score = int(sum(scores) / len(scores)) if scores else 0

    print(f"Final score: {avg_score}/100")
    return {
        "final_migrated_code": final_code,
        "score": avg_score
    }

# ── Decision: After Reviewer ──────────────────────────────────────────
def decide_after_review(state: MigrationState) -> str:
    score = state["score"]
    retry_count = state["retry_count"]
    idx = state["current_chunk_index"]
    total = len(state["chunks"])

    if score >= 80:
        # Chunk passed — check if more chunks remain
        if idx + 1 < total:
            return "next_chunk"   # more chunks to process
        else:
            return "reassemble"   # all chunks done
    elif retry_count < 2:
        return "retry"            # retry this chunk
    else:
        # Max retries — accept and move on
        if idx + 1 < total:
            return "next_chunk"
        else:
            return "reassemble"

# ── Decision: Retry or Next Chunk ─────────────────────────────────────
def increment_retry(state: MigrationState) -> dict:
    return {"retry_count": state["retry_count"] + 1}

# ── Build Graph ───────────────────────────────────────────────────────
def build_graph():
    graph = StateGraph(MigrationState)

    # Add all nodes
    graph.add_node("detector", run_detector)
    graph.add_node("chunker", run_chunker)
    graph.add_node("analyser", run_analyser)
    graph.add_node("migrator", run_migrator)
    graph.add_node("reviewer", run_reviewer)
    graph.add_node("save_chunk", save_chunk_result)
    graph.add_node("reassembler", run_reassembler)
    graph.add_node("increment_retry", increment_retry)

    # Flow
    graph.set_entry_point("detector")
    graph.add_edge("detector", "chunker")
    graph.add_edge("chunker", "analyser")
    graph.add_edge("analyser", "migrator")
    graph.add_edge("migrator", "reviewer")

    # After reviewer — decide what to do
    graph.add_conditional_edges(
        "reviewer",
        decide_after_review,
        {
            "next_chunk": "save_chunk",
            "reassemble": "save_chunk",
            "retry": "increment_retry"
        }
    )

    # After saving chunk — go to analyser for next chunk or reassemble
    graph.add_conditional_edges(
        "save_chunk",
        lambda state: "reassemble" if state["current_chunk_index"] >= len(state["chunks"]) else "analyser",
        {
            "analyser": "analyser",
            "reassemble": "reassembler"
        }
    )

    graph.add_edge("increment_retry", "migrator")
    graph.add_edge("reassembler", END)

    return graph.compile()

# ── Main Entry Point ──────────────────────────────────────────────────


def run_migration_pipeline(code: str) -> dict:
    
    # Validate before doing anything
    validation = validate_code_input(code)
    
    if not validation["valid"]:
        # Return immediately without calling any agents
        # No tokens wasted
        print(f"\nValidation failed: {validation['reason']}")
        return {
            "original_code": code,
            "language_info": {},
            "chunks": [],
            "current_chunk_index": 0,
            "migrated_chunks": [],
            "analysis": {},
            "migrated_code": "",
            "review": {},
            "score": 0,
            "retry_count": 0,
            "final_migrated_code": "",
            "all_reviews": [],
            "best_migrated_code": "",
            "best_score": 0,
            "validation_error": validation["reason"]  # ← error message
        }
    
    # Print any warnings but continue
    for warning in validation["warnings"]:
        print(f"⚠️  Warning: {warning}")
    
    graph = build_graph()

    initial_state = {
        "original_code": code,
        "language_info": {},
        "chunks": [],
        "current_chunk_index": 0,
        "migrated_chunks": [],
        "analysis": {},
        "migrated_code": "",
        "review": {},
        "score": 0,
        "retry_count": 0,
        "final_migrated_code": "",
        "all_reviews": [],
        "best_migrated_code": "",
        "best_score": 0,
        "validation_error": ""
    }

    return graph.invoke(initial_state)