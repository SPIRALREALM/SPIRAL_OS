from __future__ import annotations

"""Suggest mutations to the intent matrix based on insight metrics."""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

INSIGHT_FILE = Path(__file__).resolve().parent / "insight_matrix.json"
INTENT_FILE = Path(__file__).resolve().parent / "intent_matrix.json"
MUTATION_FILE = Path("data") / "mutations.txt"


def load_insights(path: Path = INSIGHT_FILE) -> Dict[str, Any]:
    """Return insights from ``path`` or an empty mapping."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_intents(path: Path = INTENT_FILE) -> Dict[str, Any]:
    """Return intent matrix data from ``path`` or an empty mapping."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def propose_mutations(insight_matrix: dict) -> List[str]:
    """Return mutation suggestions based on ``insight_matrix``."""
    intents = load_intents()
    rates: Dict[str, tuple[float, int]] = {}
    for pattern, info in insight_matrix.items():
        counts = info.get("counts", {})
        total = counts.get("total", 0)
        success = counts.get("success", 0)
        rate = success / total if total else 0.0
        rates[pattern] = (rate, total)

    high_quality = [p for p, (r, _) in rates.items() if r >= 0.8]
    best = max(high_quality, key=lambda p: rates[p][0]) if high_quality else None

    proposals: List[str] = []
    for pattern, (rate, total) in rates.items():
        if total < 3 or rate >= 0.5:
            continue
        synonyms = intents.get(pattern, {}).get("synonyms", [])
        if synonyms:
            proposals.append(
                f"Replace '{pattern}' with synonym '{synonyms[0]}'"
            )
        elif best and best != pattern:
            proposals.append(
                f"Merge '{pattern}' with high performer '{best}'"
            )
    return proposals


def main() -> None:
    parser = argparse.ArgumentParser(description="Suggest intent mutations")
    parser.add_argument(
        "--run",
        action="store_true",
        help="Write suggestions to data/mutations.txt",
    )
    args = parser.parse_args()

    insights = load_insights()
    suggestions = propose_mutations(insights)
    if args.run:
        MUTATION_FILE.parent.mkdir(parents=True, exist_ok=True)
        MUTATION_FILE.write_text("\n".join(suggestions), encoding="utf-8")
        print(f"Wrote {len(suggestions)} suggestions to {MUTATION_FILE}")
    else:
        for s in suggestions:
            print(s)


if __name__ == "__main__":
    main()

__all__ = ["propose_mutations"]
