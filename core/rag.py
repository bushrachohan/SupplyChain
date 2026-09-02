"""
core/rag.py

RAG (Retrieval-Augmented Generation) over the real business/procurement/
inventory policy documents in policies/*.md.

Design notes (per progress.md rules):
- Chunking is section-aware, not fixed-size. Policy docs are structured as
  H1 title + metadata block + one or more H2 ("## N. Section Name")
  sections, each a self-contained rule (confirmed against the real
  policies/inventory_policy.md). Splitting on H2 boundaries keeps each
  chunk a coherent, individually-retrievable policy rule instead of an
  arbitrary token window that could cut a rule in half.
- Uses ChromaDB (persistent, local) + sentence-transformers
  (all-MiniLM-L6-v2), per the finalized tech stack in progress.md Section 2.
- This module only retrieves and returns policy text + metadata. It does
  NOT call any LLM and does NOT decide what the agent should do with the
  retrieved policies — that constraint-application logic belongs to
  agent/orchestrator.py, per the LLM Grounding Constraint in Section 1.
"""

import re
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.utils import embedding_functions

DEFAULT_POLICIES_DIR = "policies"
DEFAULT_PERSIST_DIR = "chroma_db"
DEFAULT_COLLECTION_NAME = "policies"
DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def parse_policy_markdown(filepath: Path) -> list[dict]:
    """
    Parse one policy markdown file into section-level chunks.

    Expected structure (matches real policies/*.md files):
        # Document Title
        **Document ID:** POL-XXX-000
        ...metadata...
        ## 1. Section Name
        ...section body...
        ## 2. Another Section
        ...section body...

    Returns:
        List of chunk dicts: {chunk_id, text, doc_title, document_id,
        section_title, source_file}
    """
    raw = filepath.read_text(encoding="utf-8")

    title_match = re.search(r"^#\s+(.+)$", raw, re.MULTILINE)
    doc_title = title_match.group(1).strip() if title_match else filepath.stem

    doc_id_match = re.search(r"\*\*Document ID:\*\*\s*(\S+)", raw)
    document_id = doc_id_match.group(1).strip() if doc_id_match else filepath.stem

    # Split on H2 headers ("## ..."), keeping the header text.
    section_pattern = re.compile(r"^##\s+(.+)$", re.MULTILINE)
    matches = list(section_pattern.finditer(raw))

    chunks = []

    if not matches:
        # No H2 sections found (unexpected shape) — fall back to treating
        # the whole document as one chunk rather than silently dropping it.
        chunks.append(
            {
                "chunk_id": f"{filepath.stem}::full",
                "text": raw.strip(),
                "doc_title": doc_title,
                "document_id": document_id,
                "section_title": doc_title,
                "source_file": filepath.name,
            }
        )
        return chunks

    for i, match in enumerate(matches):
        section_title = match.group(1).strip()
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        section_text = raw[start:end].strip()

        chunks.append(
            {
                "chunk_id": f"{filepath.stem}::section_{i + 1}",
                "text": section_text,
                "doc_title": doc_title,
                "document_id": document_id,
                "section_title": section_title,
                "source_file": filepath.name,
            }
        )

    return chunks


def load_all_policy_chunks(policies_dir: str = DEFAULT_POLICIES_DIR) -> list[dict]:
    """
    Parse every .md file in policies_dir into section-level chunks.

    Raises:
        FileNotFoundError: if policies_dir doesn't exist.
        ValueError: if no .md files are found.
    """
    dir_path = Path(policies_dir)
    if not dir_path.exists():
        raise FileNotFoundError(f"Policies directory not found: {policies_dir}")

    md_files = sorted(dir_path.glob("*.md"))
    if not md_files:
        raise ValueError(f"No .md policy files found in: {policies_dir}")

    all_chunks = []
    for filepath in md_files:
        all_chunks.extend(parse_policy_markdown(filepath))

    return all_chunks


def _get_embedding_function(model_name: str = DEFAULT_EMBEDDING_MODEL):
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=model_name
    )


def build_policy_index(
    policies_dir: str = DEFAULT_POLICIES_DIR,
    persist_directory: str = DEFAULT_PERSIST_DIR,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    force_rebuild: bool = False,
) -> chromadb.api.models.Collection.Collection:
    """
    Build (or load, if already built and force_rebuild=False) the ChromaDB
    collection of embedded policy chunks.

    Returns:
        The ChromaDB collection, ready to query.
    """
    client = chromadb.PersistentClient(path=persist_directory)
    embedding_fn = _get_embedding_function()

    existing_names = [c.name for c in client.list_collections()]

    if collection_name in existing_names:
        if force_rebuild:
            client.delete_collection(collection_name)
        else:
            return client.get_collection(
                name=collection_name, embedding_function=embedding_fn
            )

    collection = client.create_collection(
        name=collection_name, embedding_function=embedding_fn
    )

    chunks = load_all_policy_chunks(policies_dir)

    collection.add(
        ids=[c["chunk_id"] for c in chunks],
        documents=[c["text"] for c in chunks],
        metadatas=[
            {
                "doc_title": c["doc_title"],
                "document_id": c["document_id"],
                "section_title": c["section_title"],
                "source_file": c["source_file"],
            }
            for c in chunks
        ],
    )

    return collection


def retrieve_policies(
    query: str,
    top_k: int = 3,
    policies_dir: str = DEFAULT_POLICIES_DIR,
    persist_directory: str = DEFAULT_PERSIST_DIR,
    collection_name: str = DEFAULT_COLLECTION_NAME,
) -> list[dict]:
    """
    Retrieve the top_k most relevant policy chunks for a query.

    This is the function agent/tools.py wraps as `retrieve_policies(query)`
    for the agent (per Section 3, agent/tools.py).

    Args:
        query: the situation/question to find relevant policy for, e.g.
            "SKU is low on safety stock, what's the buffer requirement?"
        top_k: number of chunks to return.

    Returns:
        List of dicts, ordered by relevance (most relevant first):
        {text, doc_title, document_id, section_title, source_file,
         relevance_score}
        relevance_score is in [0, 1], higher = more relevant (converted
        from ChromaDB's raw distance).

    Raises:
        ValueError: if query is empty.
    """
    if not query or not query.strip():
        raise ValueError("query must not be empty")

    collection = build_policy_index(
        policies_dir=policies_dir,
        persist_directory=persist_directory,
        collection_name=collection_name,
    )

    results = collection.query(query_texts=[query], n_results=top_k)

    retrieved = []
    ids = results["ids"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for chunk_id, text, meta, distance in zip(ids, documents, metadatas, distances):
        # ChromaDB's default distance is squared L2 on normalized
        # embeddings; convert to an intuitive 0-1 relevance score.
        relevance_score = max(0.0, 1.0 - (distance / 2.0))
        retrieved.append(
            {
                "chunk_id": chunk_id,
                "text": text,
                "doc_title": meta["doc_title"],
                "document_id": meta["document_id"],
                "section_title": meta["section_title"],
                "source_file": meta["source_file"],
                "relevance_score": round(relevance_score, 4),
            }
        )

    return retrieved


if __name__ == "__main__":
    # Quick manual smoke test — mirrors what
    # `uv run python core/rag.py` should show you in the terminal.
    hits = retrieve_policies("What is the safety stock buffer requirement?", top_k=2)
    for hit in hits:
        print(
            f"[{hit['relevance_score']}] {hit['source_file']} "
            f"/ {hit['section_title']}"
        )
        print(hit["text"][:150].replace("\n", " ") + "...")
        print()
