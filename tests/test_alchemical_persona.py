from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inanna_ai.personality_layers.albedo import AlchemicalPersona, State


def test_trigger_detection_and_metrics():
    persona = AlchemicalPersona()
    entity, triggers = persona.detect_state_trigger("Alice feels love and joy")
    assert entity == "person"
    assert triggers == {"affection", "joy"}
    persona.update_metrics(triggers)
    assert persona.entanglement > 0
    assert persona.shadow_balance == 0.0


def test_weighted_state_transitions():
    seq = iter([0.1, 0.6])
    persona = AlchemicalPersona(weights={s: 0.5 for s in State}, rng=lambda: next(seq))
    assert persona.state is State.NIGREDO
    persona.advance()
    assert persona.state is State.ALBEDO  # 0.1 < 0.5 -> advance
    persona.advance()
    assert persona.state is State.ALBEDO  # 0.6 > 0.5 -> stay

