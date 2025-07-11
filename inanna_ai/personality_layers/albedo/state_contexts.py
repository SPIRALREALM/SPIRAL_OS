"""Prompt templates for each alchemical state."""

CONTEXTS = {
    "nigredo": "[Nigredo] ({entity}) {text} {triggers}",
    "albedo": "[Albedo] ({entity}) {text} {triggers}",
    "rubedo": "[Rubedo] ({entity}) {text} {triggers}",
}

__all__ = ["CONTEXTS"]
