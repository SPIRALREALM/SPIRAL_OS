from __future__ import annotations

"""Automatically trigger fine-tuning based on feedback metrics."""

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

INSIGHT_FILE = Path("insight_matrix.json")
FEEDBACK_FILE = Path("data/feedback.json")

NOVELTY_THRESHOLD = 0.3
COHERENCE_THRESHOLD = 0.7


def _load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def compute_metrics(insights: dict, feedback: Iterable[dict]) -> tuple[float, float]:
    """Return novelty and coherence scores from feedback."""
    entries = list(feedback)
    if not entries:
        return 0.0, 0.0

    known = set(insights)
    intents = [e.get("intent") for e in entries if e.get("intent")]
    new = sum(1 for i in intents if i not in known)
    novelty = new / len(intents) if intents else 0.0

    scores = [e.get("response_quality", 0.0) for e in entries]
    coherence = sum(scores) / len(scores) if scores else 0.0
    return novelty, coherence


def build_dataset(feedback: Iterable[dict]) -> list[dict]:
    """Return a fine-tuning dataset from successful feedback entries."""
    dataset = []
    for entry in feedback:
        if entry.get("success") and entry.get("intent") and entry.get("action"):
            dataset.append({"prompt": entry["intent"], "completion": entry["action"]})
    return dataset


def system_idle() -> bool:
    """Return ``True`` if no training lock file exists."""
    return not Path("training.lock").exists()


def trigger_finetune(dataset: list[dict]) -> None:
    """Invoke the LLM fine-tuning API with ``dataset``."""
    import llm_api

    llm_api.fine_tune(dataset)


def main(argv: list[str] | None = None) -> None:  # pragma: no cover - CLI entry
    parser = argparse.ArgumentParser(description="Automatically retrain model")
    parser.add_argument("--run", action="store_true", help="Execute fine-tuning")
    parser.add_argument("--dry-run", action="store_true", help="Show dataset only")
    args = parser.parse_args(argv)

    insights = _load_json(INSIGHT_FILE, {})
    feedback = _load_json(FEEDBACK_FILE, [])

    novelty, coherence = compute_metrics(insights, feedback)
    print(f"Novelty: {novelty:.2f} Coherence: {coherence:.2f}")

    if novelty >= NOVELTY_THRESHOLD and coherence >= COHERENCE_THRESHOLD and system_idle():
        dataset = build_dataset(feedback)
        if args.run:
            trigger_finetune(dataset)
            print("Fine-tuning triggered")
        else:
            print(json.dumps(dataset, indent=2))
    else:
        print("Conditions not met")


if __name__ == "__main__":  # pragma: no cover - manual run
    main()
