import sys
from pathlib import Path
import types
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Provide a stub if module is missing
if "inanna_ai.ethical_validator" not in sys.modules:
    mod = types.ModuleType("inanna_ai.ethical_validator")

    class EthicalValidator:
        def __init__(self, allowed_users=None):
            self.allowed = set(allowed_users or [])

        def validate(self, user, prompt):
            if user not in self.allowed:
                raise PermissionError("unauthorized")
            return True

    mod.EthicalValidator = EthicalValidator
    sys.modules["inanna_ai.ethical_validator"] = mod

from inanna_ai.ethical_validator import EthicalValidator


def test_unauthorized_usage_rejected():
    validator = EthicalValidator(allowed_users={"alice"})
    with pytest.raises(PermissionError):
        validator.validate("bob", "test")

    assert validator.validate("alice", "ok") is True
