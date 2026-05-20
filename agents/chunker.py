import ast
import re
from typing import List

# Maximum lines per chunk
# Keeps each chunk small enough for nano to handle well
MAX_CHUNK_LINES = 80

def chunk_code(code: str, language: str) -> List[dict]:
    """
    Splits large code into logical chunks.
    Each chunk is a self-contained piece — a class, function, or block.
    Returns a list of chunks with metadata.
    """
    lines = code.strip().split('\n')
    total_lines = len(lines)

    # Small code — no chunking needed
    # Return as single chunk
    if total_lines <= MAX_CHUNK_LINES:
        return [{
            "chunk_id": 1,
            "total_chunks": 1,
            "code": code,
            "start_line": 1,
            "end_line": total_lines,
            "needs_chunking": False
        }]

    # Large code — needs chunking
    print(f"[Chunker] Code has {total_lines} lines — splitting into chunks")

    if language == "Java":
        return _chunk_by_class_and_method(code, lines)
    elif language in ["C++", "C"]:
        return _chunk_by_functions(code, lines)
    elif language == "Python":
        return _chunk_by_python_blocks(code, lines)
    else:
        # Unknown language — chunk by line count only
        return _chunk_by_lines(lines)


def _chunk_by_class_and_method(code: str, lines: List[str]) -> List[dict]:
    """
    For Java — splits at class and method boundaries.
    Keeps each class or method together as one chunk.
    """
    chunks = []
    current_chunk = []
    current_start = 1
    brace_depth = 0
    chunk_id = 1

    for i, line in enumerate(lines, 1):
        current_chunk.append(line)

        # Count opening and closing braces
        brace_depth += line.count('{') - line.count('}')

        # Good split point — we're back to top level (depth 0 or 1)
        # and chunk is getting large enough
        is_good_split = (
            brace_depth <= 1 and
            len(current_chunk) >= 30 and
            (line.strip() == '}' or line.strip() == '')
        )

        if is_good_split or i == len(lines):
            if current_chunk:
                chunks.append({
                    "chunk_id": chunk_id,
                    "total_chunks": None,  # filled in after
                    "code": '\n'.join(current_chunk),
                    "start_line": current_start,
                    "end_line": i,
                    "needs_chunking": True
                })
                chunk_id += 1
                current_start = i + 1
                current_chunk = []

    # Fill in total_chunks now we know how many there are
    total = len(chunks)
    for chunk in chunks:
        chunk["total_chunks"] = total

    return chunks if chunks else [{
        "chunk_id": 1,
        "total_chunks": 1,
        "code": code,
        "start_line": 1,
        "end_line": len(lines),
        "needs_chunking": False
    }]


def _chunk_by_functions(code: str, lines: List[str]) -> List[dict]:
    """
    For C/C++ — splits at function boundaries.
    """
    chunks = []
    current_chunk = []
    current_start = 1
    brace_depth = 0
    chunk_id = 1

    for i, line in enumerate(lines, 1):
        current_chunk.append(line)
        brace_depth += line.count('{') - line.count('}')

        # Split when we close a top-level function
        if brace_depth == 0 and len(current_chunk) >= 20 and line.strip() == '}':
            chunks.append({
                "chunk_id": chunk_id,
                "total_chunks": None,
                "code": '\n'.join(current_chunk),
                "start_line": current_start,
                "end_line": i,
                "needs_chunking": True
            })
            chunk_id += 1
            current_start = i + 1
            current_chunk = []

    # Add remaining lines
    if current_chunk:
        chunks.append({
            "chunk_id": chunk_id,
            "total_chunks": None,
            "code": '\n'.join(current_chunk),
            "start_line": current_start,
            "end_line": len(lines),
            "needs_chunking": True
        })

    total = len(chunks)
    for chunk in chunks:
        chunk["total_chunks"] = total

    return chunks if chunks else [{
        "chunk_id": 1, "total_chunks": 1,
        "code": code, "start_line": 1,
        "end_line": len(lines), "needs_chunking": False
    }]


def _chunk_by_python_blocks(code: str, lines: List[str]) -> List[dict]:
    """
    For Python — splits at class and function definitions (def/class keywords).
    """
    chunks = []
    current_chunk = []
    current_start = 1
    chunk_id = 1

    for i, line in enumerate(lines, 1):
        # New top-level block starting — good split point
        is_new_block = (
            (line.startswith('def ') or line.startswith('class ')) and
            len(current_chunk) >= 20
        )

        if is_new_block:
            chunks.append({
                "chunk_id": chunk_id,
                "total_chunks": None,
                "code": '\n'.join(current_chunk),
                "start_line": current_start,
                "end_line": i - 1,
                "needs_chunking": True
            })
            chunk_id += 1
            current_start = i
            current_chunk = []

        current_chunk.append(line)

    if current_chunk:
        chunks.append({
            "chunk_id": chunk_id,
            "total_chunks": None,
            "code": '\n'.join(current_chunk),
            "start_line": current_start,
            "end_line": len(lines),
            "needs_chunking": True
        })

    total = len(chunks)
    for chunk in chunks:
        chunk["total_chunks"] = total

    return chunks if chunks else [{
        "chunk_id": 1, "total_chunks": 1,
        "code": code, "start_line": 1,
        "end_line": len(lines), "needs_chunking": False
    }]


def _chunk_by_lines(lines: List[str]) -> List[dict]:
    """
    Fallback — just split every MAX_CHUNK_LINES lines.
    Used when language is unknown.
    """
    chunks = []
    chunk_id = 1

    for i in range(0, len(lines), MAX_CHUNK_LINES):
        chunk_lines = lines[i:i + MAX_CHUNK_LINES]
        chunks.append({
            "chunk_id": chunk_id,
            "total_chunks": None,
            "code": '\n'.join(chunk_lines),
            "start_line": i + 1,
            "end_line": i + len(chunk_lines),
            "needs_chunking": True
        })
        chunk_id += 1

    total = len(chunks)
    for chunk in chunks:
        chunk["total_chunks"] = total

    return chunks


def reassemble_chunks(migrated_chunks: List[str]) -> str:
    """
    Takes all migrated chunks and joins them back into one file.
    Adds a blank line between chunks for readability.
    """
    return '\n\n'.join(chunk.strip() for chunk in migrated_chunks)