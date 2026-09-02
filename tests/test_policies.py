"""
Unit tests for business policies in policies/ directory.
Verifies policy documents exist, are non-empty, and contain required policy header structures.
"""

import os
import glob
import pytest


def test_policies_directory_exists():
    """Verify policies directory exists and contains markdown files."""
    assert os.path.exists("policies")
    policy_files = glob.glob("policies/*.md")
    assert len(policy_files) >= 3


def test_policy_files_content():
    """Verify each policy file has valid structure and header metadata."""
    policy_files = glob.glob("policies/*.md")
    required_keywords = ["Document ID:", "Version:", "Effective Date:"]

    for file_path in policy_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert len(content.strip()) > 100
            for keyword in required_keywords:
                assert keyword in content, f"Missing '{keyword}' in {file_path}"
