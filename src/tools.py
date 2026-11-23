"""Outils partagés : utilisés par le graphe LangGraph ET exposés par le serveur MCP."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


def run_tests(code: str, timeout: int = 60) -> dict:
    """Exécute du code pytest dans un répertoire temporaire et renvoie un résumé."""
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "test_generated.py").write_text(code, encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "--tb=short", "-p", "no:cacheprovider", tmp],
            capture_output=True, text=True, timeout=timeout,
        )
    summary = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    passed = _count(summary, "passed")
    failed = _count(summary, "failed")
    return {"passed": passed, "failed": failed, "total": passed + failed, "exit_code": proc.returncode, "summary": summary}


def _count(summary: str, word: str) -> int:
    parts = summary.replace(",", " ").split()
    for i, p in enumerate(parts):
        if p == word and i > 0 and parts[i - 1].isdigit():
            return int(parts[i - 1])
    return 0
