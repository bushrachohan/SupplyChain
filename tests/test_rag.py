"""
tests/test_rag.py

Per Section 9 (Testing Strategy): "core/rag.py — safety stock query
retrieves safety-stock policy document."

Uses a temporary policies dir + temporary Chroma persist dir per test run,
so tests don't depend on or pollute the real policies/ or chroma_db/.
"""

import shutil

import pytest

from core.rag import (
    load_all_policy_chunks,
    parse_policy_markdown,
    retrieve_policies,
)

REAL_INVENTORY_POLICY = """# Inventory Control & Safety Stock Policy

**Document ID:** POL-INV-001
**Version:** 1.0
**Effective Date:** 2026-06-01
**Target Scope:** Global Warehouses & Regional Distribution Centers

---

## 1. Safety Stock Buffer Requirements

1. **Tier-1 Critical SKUs (High Value / High Velocity):**
   - Must maintain a minimum of **14 days (2 weeks)** of safety stock buffer based on trailing 4-week mean daily demand.
   - If stock falls below 14 days, an immediate **INVENTORY_RISK_FLAG** (CRITICAL) must be raised.

2. **Tier-2 Standard SKUs:**
   - Must maintain a minimum of **7 days (1 week)** of safety stock buffer.
   - Stock below 7 days triggers a **REORDER_WARNING** (MEDIUM).

3. **Tier-3 Low Velocity SKUs:**
   - Safety stock buffer requirement is **3 days**.

---

## 2. Reorder Point (ROP) Calculation Policy

- Reorder Point formula: ROP = (Lead Time in Days x Average Daily Demand) + Safety Stock
- Purchase orders must be automatically recommended whenever current_stock <= ROP.

---

## 3. Stockout Prevention & Allocation Constraints

- **Zero-Stock Penalty:** Any projected stockout within 7 days requires emergency stock re-allocation from the nearest regional warehouse before expediting external purchase orders.
- **Max Stock Cap:** Inventory levels must not exceed **60 days of demand** to prevent warehouse congestion and holding costs.
"""

UNRELATED_LOGISTICS_POLICY = """# Carrier & Route Policy

**Document ID:** POL-LOG-001

## 1. Carrier Scorecards

Carriers are scored quarterly on on-time delivery rate and damage claims.

## 2. Fuel Surcharge Handling

Fuel surcharges are recalculated monthly based on published index rates.
"""


@pytest.fixture
def policies_dir(tmp_path):
    d = tmp_path / "policies"
    d.mkdir()
    (d / "inventory_policy.md").write_text(REAL_INVENTORY_POLICY, encoding="utf-8")
    (d / "logistics_policy.md").write_text(
        UNRELATED_LOGISTICS_POLICY, encoding="utf-8"
    )
    return str(d)


@pytest.fixture
def chroma_dir(tmp_path):
    d = tmp_path / "chroma_db"
    yield str(d)
    shutil.rmtree(d, ignore_errors=True)


def test_parse_policy_markdown_splits_by_h2_section(tmp_path):
    filepath = tmp_path / "inventory_policy.md"
    filepath.write_text(REAL_INVENTORY_POLICY, encoding="utf-8")

    chunks = parse_policy_markdown(filepath)

    assert len(chunks) == 3
    assert chunks[0]["section_title"] == "1. Safety Stock Buffer Requirements"
    assert chunks[0]["document_id"] == "POL-INV-001"
    assert chunks[0]["doc_title"] == "Inventory Control & Safety Stock Policy"
    assert "14 days" in chunks[0]["text"]
    assert chunks[1]["section_title"] == "2. Reorder Point (ROP) Calculation Policy"
    assert chunks[2]["section_title"] == "3. Stockout Prevention & Allocation Constraints"


def test_load_all_policy_chunks_reads_every_md_file(policies_dir):
    chunks = load_all_policy_chunks(policies_dir)
    source_files = {c["source_file"] for c in chunks}
    assert source_files == {"inventory_policy.md", "logistics_policy.md"}
    assert len(chunks) == 5  # 3 inventory sections + 2 logistics sections


def test_load_all_policy_chunks_missing_dir_raises():
    with pytest.raises(FileNotFoundError):
        load_all_policy_chunks("policies_that_do_not_exist")


def test_safety_stock_query_retrieves_safety_stock_policy(policies_dir, chroma_dir):
    results = retrieve_policies(
        query="What is the safety stock buffer requirement for critical SKUs?",
        top_k=1,
        policies_dir=policies_dir,
        persist_directory=chroma_dir,
    )

    assert len(results) == 1
    top_hit = results[0]
    assert top_hit["source_file"] == "inventory_policy.md"
    assert top_hit["section_title"] == "1. Safety Stock Buffer Requirements"
    assert "14 days" in top_hit["text"]
    assert 0.0 <= top_hit["relevance_score"] <= 1.0


def test_reorder_point_query_retrieves_rop_section(policies_dir, chroma_dir):
    results = retrieve_policies(
        query="How is the reorder point calculated?",
        top_k=1,
        policies_dir=policies_dir,
        persist_directory=chroma_dir,
    )

    assert results[0]["section_title"] == "2. Reorder Point (ROP) Calculation Policy"


def test_retrieve_policies_empty_query_raises(policies_dir, chroma_dir):
    with pytest.raises(ValueError):
        retrieve_policies(
            query="",
            policies_dir=policies_dir,
            persist_directory=chroma_dir,
        )


def test_retrieve_policies_returns_results_ordered_by_relevance(policies_dir, chroma_dir):
    results = retrieve_policies(
        query="safety stock",
        top_k=3,
        policies_dir=policies_dir,
        persist_directory=chroma_dir,
    )

    assert len(results) == 3
    scores = [r["relevance_score"] for r in results]
    assert scores == sorted(scores, reverse=True)
