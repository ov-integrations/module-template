# Contributing to module-template

Thank you for taking the time to contribute.  This document describes the
development workflow, coding standards, and review process.

## Table of contents

1. [Development environment](#development-environment)
2. [Branching strategy](#branching-strategy)
3. [Coding standards](#coding-standards)
4. [Testing requirements](#testing-requirements)
5. [Commit messages](#commit-messages)
6. [Pull request process](#pull-request-process)
7. [CI pipeline](#ci-pipeline)

---

## Development environment

### Required tools

| Tool | Minimum version | Install |
|------|----------------|---------|
| Python | 3.10 | [python.org](https://www.python.org/downloads/) |
| uv | 0.3 | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| git | 2.x | system package manager |

### Setup

```bash
# 1. Fork and clone
git clone https://github.com/ov-integrations/module-template.git
cd module-template

# 2. Create a virtual environment with uv
uv venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install project and dev dependencies
uv pip install -e ".[dev]"

# 4. Verify everything works
ruff check .
pytest
```

---

## Branching strategy

- `master` is the stable branch; direct pushes are not permitted.
- Create a feature branch named after the ticket: `API-XXXXXX` or
  `FEATURE-description`.
- Keep branches short-lived and focused on a single concern.
- Rebase onto `master` before opening a PR to keep history linear.

```bash
git checkout master
git pull origin master
git checkout -b API-123456
```

---

## Coding standards

All Python code in this repository must pass `ruff check .` with zero errors.

### Type hints

Every function signature **must** carry type hints, including return types:

```python
# Good
def load_json_file(path: Path) -> dict[str, Any]: ...

# Bad — missing return type
def load_json_file(path):  ...
```

Use `from __future__ import annotations` at the top of every module to enable
deferred evaluation of annotations (PEP 563).

### Docstrings

Use Google-style docstrings for all public functions, methods, and classes:

```python
def validate_settings(settings_data: dict[str, Any], schema: dict[str, Any]) -> None:
    """Validate settings_data against a JSON Schema.

    Args:
        settings_data: The settings dictionary loaded from settings.json.
        schema: The JSON Schema dictionary loaded from settings_schema.json.

    Raises:
        ValueError: If validation fails.
    """
```

Private helpers (prefixed with `_`) should still have a one-line docstring
describing intent.

### File I/O

Always use `pathlib.Path` for paths and context managers for file access:

```python
# Good
with path.open(encoding="utf-8") as fh:
    data = json.load(fh)

# Bad — manual open/close and legacy string paths
f = open("file.json")
data = json.loads(f.read())
f.close()
```

### Error handling

- Catch specific exception types; avoid bare `except:` or `except Exception:`
  unless you immediately re-raise.
- Wrap lower-level exceptions with contextual messages using `raise ... from`:

```python
try:
    validate(instance=data, schema=schema)
except ValidationError as exc:
    raise ValueError(f"Settings invalid: {exc}") from exc
```

- Add `logging.exception(...)` before re-raising so the traceback appears in
  the log.

### Logging

Use the module-level logger (never `print`):

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Starting process")
logger.debug("Loaded %d records", len(records))
logger.exception("Unexpected error during sync")  # includes traceback
```

---

## Testing requirements

- All new code must have accompanying tests in `tests/`.
- The project enforces **80% minimum coverage**; aim for 100% on core paths.
- Tests are tagged with `@pytest.mark.unit` (no I/O) or
  `@pytest.mark.integration` (filesystem/network).
- Use `tmp_path` (pytest built-in) for any tests that write files.
- Mock external calls (`subprocess`, `IntegrationLog`, network) in unit tests.

### Running the suite

```bash
# Full suite
pytest

# Only unit tests
pytest -m unit

# Only integration tests
pytest -m integration

# With verbose output
pytest -v

# With HTML coverage report
pytest --cov-report=html && open htmlcov/index.html
```

### Writing tests

Use class-based grouping for related tests and descriptive method names:

```python
class TestModuleStart:
    @pytest.mark.unit()
    def test_logs_info_message_on_success(self, mock_log: MagicMock) -> None:
        """start() must emit a INFO log entry."""
        module = Module(mock_log, {})
        module.start()
        mock_log.add.assert_called_once_with(LogLevel.INFO, "Module is started")
```

---

## Commit messages

Follow the Conventional Commits format where possible:

```
<type>(<scope>): <short summary>

<optional body>
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ci`

Examples:

```
feat(module): add retry logic for API calls

fix(start_module): correct typo in exception variable name

test(conftest): add fixture for invalid settings file

chore: bump jsonschema to 4.23.0
```

Keep the summary line under 72 characters.

---

## Pull request process

1. Ensure `ruff check .` and `pytest` both pass locally before pushing.
2. Push to your branch and open a PR against `master`.
3. Fill in the PR template (summary, test plan, screenshots if applicable).
4. Address all review comments before requesting re-review.
5. Squash or rebase if the CI asks you to.
6. A maintainer will merge once all checks are green.

---

## CI pipeline

Every pull request triggers the CI workflow (`.github/workflows/ci.yml`):

| Job | Tool | Failure condition |
|-----|------|------------------|
| Lint | `ruff check .` | Any violation |
| Format | `ruff format --check .` | Any unformatted file |
| Test | `pytest` | Any failing test or coverage < 80% |

Fix all failures before requesting a review.
