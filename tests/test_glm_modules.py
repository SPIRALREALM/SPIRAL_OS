import sys
from types import ModuleType
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from INANNA_AI import glm_init, glm_analyze


class DummyResponse:
    def __init__(self, data: dict[str, str]):
        self._data = data
        self.text = data.get('summary') or data.get('analysis', '')

    def json(self):
        return self._data


def test_glm_init_summarize(tmp_path, monkeypatch):
    readme = tmp_path / 'README.md'
    qnl = tmp_path / 'QNL_LANGUAGE'
    qnl.mkdir()
    readme.write_text('hello', encoding='utf-8')
    (qnl / 'a.md').write_text('world', encoding='utf-8')

    out_dir = tmp_path / 'audit_logs'

    monkeypatch.setattr(glm_init, 'ROOT', tmp_path)
    monkeypatch.setattr(glm_init, 'README_FILE', readme)
    monkeypatch.setattr(glm_init, 'QNL_DIR', qnl)
    monkeypatch.setattr(glm_init, 'AUDIT_DIR', out_dir)
    monkeypatch.setattr(glm_init, 'PURPOSE_FILE', out_dir / 'purpose.txt')

    dummy = ModuleType('requests')
    dummy.post = lambda *a, **k: DummyResponse({'summary': 'sum'})
    monkeypatch.setattr(glm_init, 'requests', dummy)

    summary = glm_init.summarize_purpose()
    assert summary == 'sum'
    assert (out_dir / 'purpose.txt').read_text() == 'sum'


def test_glm_analyze_code(tmp_path, monkeypatch):
    code_dir = tmp_path / 'inanna_ai'
    code_dir.mkdir()
    (code_dir / 'x.py').write_text('print(1)', encoding='utf-8')

    out_dir = tmp_path / 'audit_logs'

    monkeypatch.setattr(glm_analyze, 'ROOT', tmp_path)
    monkeypatch.setattr(glm_analyze, 'CODE_DIR', code_dir)
    monkeypatch.setattr(glm_analyze, 'AUDIT_DIR', out_dir)
    monkeypatch.setattr(glm_analyze, 'ANALYSIS_FILE', out_dir / 'code_analysis.txt')

    dummy = ModuleType('requests')
    dummy.post = lambda *a, **k: DummyResponse({'analysis': 'ok'})
    monkeypatch.setattr(glm_analyze, 'requests', dummy)

    analysis = glm_analyze.analyze_code()
    assert analysis == 'ok'
    assert (out_dir / 'code_analysis.txt').read_text() == 'ok'
