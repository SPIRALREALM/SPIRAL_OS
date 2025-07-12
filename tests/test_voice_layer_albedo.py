import sys
import types

sys.modules.setdefault("opensmile", types.ModuleType("opensmile"))
sys.modules.setdefault("EmotiVoice", types.ModuleType("EmotiVoice"))
sys.modules.setdefault("numpy", types.ModuleType("numpy"))
sys.modules.setdefault("librosa", types.ModuleType("librosa"))
sys.modules.setdefault("soundfile", types.ModuleType("soundfile"))
sys.modules.setdefault("openvoice", types.ModuleType("openvoice"))
sys.modules.setdefault("gtts", types.ModuleType("gtts"))
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from inanna_ai import voice_layer_albedo, voice_evolution


def test_modulate_voice_adds_preset_and_calls_synth(monkeypatch):
    calls = {}

    def fake_synth(text: str, tone: str, history=None, timbre='neutral'):
        calls['args'] = (text, tone)
        return 'out.wav'

    monkeypatch.setattr(voice_layer_albedo.speaking_engine, 'synthesize_speech', fake_synth)

    path = voice_layer_albedo.modulate_voice('hello', 'lunar')
    assert path == 'out.wav'
    assert calls['args'] == ('hello', 'lunar')
    assert voice_evolution.get_voice_params('lunar') == voice_layer_albedo.TONE_PRESETS['lunar']


def test_modulate_voice_unknown_tone(monkeypatch):
    monkeypatch.setattr(voice_layer_albedo.speaking_engine, 'synthesize_speech', lambda t, e: 'x.wav')
    before = dict(voice_evolution._evolver.styles)
    path = voice_layer_albedo.modulate_voice('hi', 'mystic')
    assert path == 'x.wav'
    assert 'mystic' not in voice_evolution._evolver.styles
    voice_evolution._evolver.styles = before


