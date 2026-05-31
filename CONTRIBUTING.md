# Contributing

Thanks for helping improve `maintainer-health`.

## Setup

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

## Pull Requests

Please include:

- A short summary of the change.
- Tests for new checks or CLI behavior.
- Notes about false positives or tradeoffs.

Keep new checks offline-first unless a feature explicitly adds optional network enrichment.
