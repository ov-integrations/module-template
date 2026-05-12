# module-template

Template repository for creating new OneVizion integration modules.

## Overview

This template provides the standard skeleton for a Python-based OneVizion
integration module.  It includes:

- `module.py` — the class that holds your integration logic
- `start_module.py` — the entry-point script executed by the iHub platform
- `settings.json` — user-supplied configuration (URL, API keys)
- `settings_schema.json` — JSON Schema that validates `settings.json`
- `pyproject.toml` — modern Python project config (dependencies, tooling)
- `tests/` — pytest suite with fixtures covering core functionality

## Quick start

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | ≥ 3.10 | Runtime |
| [uv](https://docs.astral.sh/uv/) | ≥ 0.3 | Dependency management |
| [ruff](https://docs.astral.sh/ruff/) | ≥ 0.5 | Linting and formatting |

Install `uv` (if not already present):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Clone and set up

```bash
# Clone the repository (or use it as a template on GitHub)
git clone https://github.com/ov-integrations/module-template.git my-module
cd my-module

# Create a virtual environment and install all dependencies
uv venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### Configure settings

Copy and fill in `settings.json`:

```json
{
  "ovUrl": "https://your-org.onevizion.com",
  "ovAccessKey": "<20-character access key>",
  "ovSecretKey": "<70-character secret key>"
}
```

The values are validated against `settings_schema.json` at startup. The file
**must not be committed** — it is listed in `.gitignore`.

## Compatibility & Requirements

### OneVizion iHub Environment

| Component | Requirement | Notes |
|-----------|-------------|-------|
| **iHub version** | ≥ 24.7.0 (recommended) | Older versions may work but verify uv availability |
| **Python** | ≥ 3.10 | Required for modern type hint syntax |
| **uv or pip** | Either available | Module falls back to pip if uv not found |

### Dependency Installation Strategy

The module automatically handles dependencies with a smart fallback chain:

1. **Try `uv`**: Fast, modern dependency resolution (if available in PATH)
2. **Auto-install `uv`**: If not found, automatically installs to `~/.local/bin`
3. **Fallback to `pip`**: If `uv` installation fails or no internet, uses standard `pip`

This "try and auto-install" approach ensures:
- ✅ Fast installation with `uv` when possible
- ✅ Automatic setup without manual intervention
- ✅ Works on any Linux distribution
- ✅ No sudo required
- ✅ Graceful degradation to `pip` if needed

### Migrating Existing Modules

If you have existing modules using `python_dependencies.txt` or `python_dependencies.ini`:

**Option 1: Full Migration (Recommended)**
1. Create `pyproject.toml` with dependencies from your `.txt`/`.ini` file
2. Replace installation logic in entry point with template's `install_dependencies()`
3. Adopt type hints, tests, and modern patterns incrementally

**Option 2: Hybrid Approach**
1. Keep your existing dependency file format
2. Adopt testing framework and CI/CD from template
3. Gradually refactor code style (type hints, docstrings)

**Compatibility Note**: This template uses `start_module.py` as the entry point. Production modules often use `start_integration.py`. Either name works — choose based on your organization's convention.

## Running the module

The iHub platform executes the module with:

```bash
python3 start_module.py
```

Before running locally you must also provide `ihub_parameters.json` (injected
automatically by iHub in production):

```json
{
  "processId": 12345,
  "logLevel": "INFO"
}
```

> `ihub_parameters.json` is in `.gitignore` and must never be committed.

## Development workflow

### Linting and formatting

```bash
# Check for violations (zero tolerance)
ruff check .

# Auto-fix fixable violations
ruff check --fix .

# Format all Python files
ruff format .
```

### Running tests

```bash
# Run the full suite with coverage (80% minimum enforced)
pytest

# Run only unit tests (no filesystem I/O)
pytest -m unit

# Run integration tests
pytest -m integration

# Generate an HTML coverage report
pytest --cov-report=html
open htmlcov/index.html
```

### Type checking

```bash
mypy module.py start_module.py
```

## Project structure

```
module-template/
├── .github/
│   └── workflows/
│       ├── ci.yml               # Lint, type-check, and test on every PR
│       ├── create-release.yml   # Automated release workflow
│       └── run-module-tests.yml # Full UI/integration test suite
├── documents/                   # Images and docs referenced in READMEs
├── installation/                # OneVizion installation XML and SQL scripts
├── tests/
│   ├── conftest.py              # Shared pytest fixtures
│   ├── test_module.py           # Unit tests for module.py
│   └── test_start_module.py     # Unit + integration tests for start_module.py
├── uninstallation/              # Cleanup SQL scripts
├── .gitignore
├── .integration_                # Rename to .integration to enable UI listing
├── module.py                    # Integration business logic (edit this)
├── pyproject.toml               # Project metadata, dependencies, tool config
├── README.md
├── settings.json                # Runtime config (not committed)
├── settings_schema.json         # JSON Schema for settings validation
└── start_module.py              # Entry-point (rarely needs editing)
```

## Implementing a module

1. Open `module.py`.
2. Replace the body of `Module.start()` with your integration logic.
3. Add any helper methods as private methods (prefixed with `_`).
4. Add fields to `settings.json` and update `settings_schema.json` to validate them.
5. Write tests in `tests/test_module.py`.

```python
# Example: extended Module.start()
def start(self) -> None:
    url = self._settings["ovUrl"]
    self._module_log.add(LogLevel.INFO, f"Connecting to {url}")
    # ... your logic here
```

## Configuration reference

### settings.json

| Field | Type | Description |
|-------|------|-------------|
| `ovUrl` | string | Base URL of your OneVizion instance, must start with `https://` |
| `ovAccessKey` | string | 20-character API access key |
| `ovSecretKey` | string | 70-character API secret key |

### .integration_ file

Rename `.integration_` to `.integration` to make the module visible in the
OneVizion iHub UI module list.

## Python style guidelines

This project follows [PEP 8](https://peps.python.org/pep-0008/) and is
enforced by `ruff`.  Key conventions:

- All public functions and classes must have Google-style docstrings.
- All function signatures must carry type hints.
- Use `pathlib.Path` for all filesystem paths.
- Prefer `with` context managers for all file/resource handling.
- Specific exception types with clear messages; never bare `except:`.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full development guide.
