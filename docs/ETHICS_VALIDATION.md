# Ethics Validation

`EthicalValidator` inspects prompts before they reach the language models. Keyword scanning is combined with a semantic layer powered by optional [SentenceTransformer](https://www.sbert.net/) models.

## Semantic Categories

The validator embeds configured phrases for categories such as **explicit harm**, **lack of consent**, and **bias**. A prompt's embedding is compared to these phrases and any category exceeding the similarity threshold triggers rejection.

```python
validator = EthicalValidator(banned_categories={"harm": ["cause injury"]}, threshold=0.6)
```

If the sentence‑transformers library is unavailable, only keyword checks run.

## Context Awareness

Use `inanna_ai.context_awareness` to record recent interactions and supply them
when validating a prompt:

```python
from inanna_ai.context_awareness import record_interaction, retrieve_context
from inanna_ai.ethical_validator import EthicalValidator

record_interaction("hello world")
context = retrieve_context(5)
validator.validate("alice", "be nice", recent_context=context)
```

The context texts are appended before the semantic check so violations can be
detected across the conversation history.
