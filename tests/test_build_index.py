"""
Unit tests for scripts/build_index.py — chunking logic only.
No API calls are made; these run cleanly in CI without any keys.
"""
import sys
from pathlib import Path

# Allow importing scripts/ as a package from the repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.build_index import CHUNK_SIZE, OVERLAP, chunk_text  # noqa: E402


def test_chunk_text_produces_multiple_chunks():
    """A text longer than CHUNK_SIZE words must yield at least two chunks."""
    text = " ".join(["word"] * (CHUNK_SIZE * 2))
    chunks = chunk_text(text, source="test.pdf", page=1)
    assert len(chunks) >= 2


def test_chunk_text_respects_max_size():
    """No individual chunk should exceed CHUNK_SIZE words."""
    text = " ".join(["w"] * 1200)
    chunks = chunk_text(text, source="test.pdf", page=1)
    for chunk in chunks:
        assert len(chunk["text"].split()) <= CHUNK_SIZE


def test_chunk_text_metadata_fields():
    """Every chunk must carry source, page, and chunk_id."""
    chunks = chunk_text("hello world " * 20, source="sample.pdf", page=3)
    for chunk in chunks:
        assert chunk["source"] == "sample.pdf"
        assert chunk["page"] == 3
        assert "chunk_id" in chunk
        assert chunk["chunk_id"].startswith("sample.pdf_p3_c")


def test_chunk_text_empty_input():
    """Empty or whitespace-only text should produce no chunks."""
    assert chunk_text("", source="x.pdf", page=1) == []
    assert chunk_text("   \n\t  ", source="x.pdf", page=1) == []


def test_chunk_text_overlap():
    """Adjacent chunks should share at least OVERLAP words."""
    words = [f"w{i}" for i in range(CHUNK_SIZE + OVERLAP + 20)]
    chunks = chunk_text(" ".join(words), source="t.pdf", page=1)
    if len(chunks) >= 2:
        set0 = set(chunks[0]["text"].split())
        set1 = set(chunks[1]["text"].split())
        assert len(set0 & set1) >= OVERLAP, "Adjacent chunks must overlap by at least OVERLAP words"


def test_chunk_text_chunk_id_unique():
    """chunk_id values must be unique across all chunks."""
    text = " ".join(["tok"] * 2000)
    chunks = chunk_text(text, source="big.pdf", page=1)
    ids = [c["chunk_id"] for c in chunks]
    assert len(ids) == len(set(ids)), "chunk_ids must be unique"
