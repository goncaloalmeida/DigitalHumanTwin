# Digital Human Twin

Minimal Python/PySide6 base for a future digital human twin application.

## Goal

- Start with a clean desktop architecture
- Keep the codebase small
- Add future features inside `src/modules`

## Tech

- Python 3.10+
- PySide6 (Qt for Python)

## Structure

```text
src/
  app/
  core/
  modules/
  main.py
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python src/main.py
```

## Current module capabilities

- Body profile selection (Male, Female, Neutral)
- Add multiple body instances inside the session
- Layer-by-layer anatomy exploration from skin to heart/arteries

## Quick smoke test

```bash
python src/main.py --smoke-test
```
