# FreshBench Engineering Rules

These rules apply to every AI and engineer working on this repository.

The project is developed across different local environments:

- LingJing: ARM macOS
- Tina: x86 Windows
- Railway: Linux deployment environment

Do not treat any single local machine as the source of truth. The practical source of truth is:

```bash
uv sync
uv run pytest
Railway build/deploy
```

## 1. Cross-Platform Defaults

Use cross-platform code by default.

Required:

- Use `pathlib.Path` for all filesystem paths.
- Use relative paths from the project root.
- Keep filenames lowercase and case-consistent.
- Keep commands runnable from the repository root.
- Keep dependencies installable on macOS, Windows, and Railway/Linux.

Avoid:

- Hardcoded `/Users/...` paths.
- Hardcoded `C:\Users\...` paths.
- Shell-only assumptions such as requiring `zsh`, `bash`, or PowerShell.
- Case-mismatched imports such as importing `Schemas` when the file is `schemas.py`.

## 2. Dependency Rules

Use `uv` for Python dependency management.

Baseline commands:

```bash
uv sync
uv run pytest
uv run uvicorn apps.api.main:app --reload
```

Do not commit local virtual environments or dependency caches.

Avoid heavy or platform-fragile dependencies in v1:

- local OCR engines
- local PDF system tools
- native vector databases
- platform-specific binary wheels
- local model runtimes

If a dependency needs native compilation or external system packages, discuss it first and document the reason.

## 3. Path and File Handling

Use `pathlib` in Python.

Good:

```python
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sample_path = PROJECT_ROOT / "data" / "samples" / "good_document_asset.json"
```

Avoid:

```python
"data\\samples\\good_document_asset.json"
"data/samples/good_document_asset.json"
"/Users/ling_jing/Desktop/..."
"C:\\Users\\Tina\\..."
```

Use UTF-8 for all source, Markdown, JSON, HTML, CSS, and JavaScript files.

## 4. Git Hygiene

Do not commit machine-local files.

Never commit:

- `.venv/`
- `__pycache__/`
- `.pytest_cache/`
- `.DS_Store`
- `Thumbs.db`
- local reports under `data/reports/`
- local submissions under `data/submissions/`
- secrets or API keys

Commit allowed sample data under `data/samples/`.

Generated reports and local submissions should be reproducible, not source-controlled.

## 5. Line Endings and Case Sensitivity

Windows may create CRLF line endings. macOS and Linux usually use LF. Railway runs on Linux.

Use repository-level `.gitattributes` to normalize text files.

Important:

- Python files should use LF.
- Markdown files should use LF.
- JSON files should use LF.
- HTML/CSS/JS files should use LF.

Linux is case-sensitive. Windows and many macOS filesystems are not.

Therefore:

- Keep module filenames lowercase.
- Keep import paths exactly matching actual filenames.
- Avoid files that differ only by case.

## 6. Docker and Architecture

Do not make Docker a P0 requirement.

Reason:

- LingJing's local machine is ARM macOS.
- Tina's local machine is x86 Windows.
- Railway deploys on Linux.
- Locally built Docker images can have architecture mismatches.

For v1:

- Deploy from source on Railway.
- Do not require local Docker images.
- Do not require local model weights.

Docker can be reconsidered later for sandboxed code tasks or production validator workers.

## 7. Railway Rules

Railway is the demo hosting environment, not the full production subnet runtime.

Railway requirements:

- The app must listen on `$PORT`.
- `/health` must return a simple ok response.
- The demo must not require local model weights.
- The demo must not rely on files outside the repository.
- The static UI must use relative API paths.

Recommended local validation before deploy:

```bash
uv run pytest
uv run uvicorn apps.api.main:app --reload
```

Recommended Railway validation:

```bash
railway up
railway logs
curl https://<railway-domain>/health
```

## 8. Collaboration Rules

Read these files before starting work:

1. `PLAN.md`
2. `RULES.md`
3. your personal plan file:
   - `plan_lingjing.md`
   - `plan_tina.md`

Do not optimize only for your own task.

Each completed phase must leave the other collaborator able to continue through:

- stable schemas
- stable function signatures
- stable API paths
- sample input/output files
- validation command
- validation result
- notes for the next phase

If your change affects the other person's workstream, update:

- `PLAN.md`
- your personal plan if needed
- implementation guide if needed
- tests or sample fixtures

## 9. Completion Standard

A phase is not complete until validation evidence exists.

Minimum completion record:

```md
### YYYY-MM-DD HH:mm - Phase X completed

- AI/Engineer:
- Files changed:
- Validation command:
- Validation result:
- Cross-platform notes:
- Next step:
```

