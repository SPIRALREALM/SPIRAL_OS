# Ethics Validation

`EthicalValidator` inspects prompts before they reach the language models. Keyword scanning is combined with a semantic layer powered by optional [SentenceTransformer](https://www.sbert.net/) models.

## Semantic Categories

The validator embeds configured phrases for categories such as **explicit harm**, **lack of consent**, and **bias**. A prompt's embedding is compared to these phrases and any category exceeding the similarity threshold triggers rejection.

```python
validator = EthicalValidator(banned_categories={"harm": ["cause injury"]}, threshold=0.6)
```

If the sentence‑transformers library is unavailable, only keyword checks run.
