import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inanna_ai import voice_evolution


def test_update_from_history_modifies_style():
    evol = voice_evolution.VoiceEvolution({'joy': {'speed': 1.0, 'pitch': 0.0}})
    history = [
        {'emotion': 'joy', 'arousal': 0.7, 'valence': 0.8, 'sentiment': 0.2},
        {'emotion': 'joy', 'arousal': 0.8, 'valence': 0.6, 'sentiment': 0.4},
    ]
    evol.update_from_history(history)
    arousal = float(np.mean([0.7, 0.8]))
    valence = float(np.mean([0.8, 0.6]))
    sentiment = float(np.mean([0.2, 0.4]))
    new_speed = round(1.0 + (arousal - 0.5) * 0.4, 3)
    new_pitch = round((valence - 0.5) * 2.0, 3)
    weight = 1.0 + sentiment
    exp_speed = round((1.0 + new_speed * weight) / (1.0 + weight), 3)
    exp_pitch = round((0.0 + new_pitch * weight) / (1.0 + weight), 3)
    assert evol.styles['joy']['speed'] == exp_speed
    assert evol.styles['joy']['pitch'] == exp_pitch


def test_get_params_returns_default_for_unknown():
    evol = voice_evolution.VoiceEvolution()
    params = evol.get_params('unknown')
    assert params == evol.styles['neutral']
