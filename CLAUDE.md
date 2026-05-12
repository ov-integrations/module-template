# Claude Code Context: OneVizion Module Template

## Project Overview

This is a modern Python template for creating OneVizion integration modules. The template incorporates best practices for type safety, testing, and maintainability.

### Purpose
- Foundation for new OneVizion iHub integration modules
- Demonstration of modern Python development patterns (type hints, testing, CI/CD)
- Maintainable, production-ready starting point

### Target Platform
- **OneVizion iHub**: Integration Hub platform (version 24.7.0+)
- **Python**: 3.10+ required
- **Deployment**: Runs as scheduled modules within OneVizion's iHub environment

## Architecture & Patterns

### Core Design Principles

1. **Separation of Concerns**
   - `Module` class contains business logic, isolated and testable
   - `start_module.py` is the entry point handling dependency management and orchestration
   - Logic stays separate from infrastructure

2. **Dependency Injection**
   - `Module.__init__` receives `IntegrationLog` and settings dict
   - Testing works easily with mock objects
   - Tight coupling to OneVizion internals is avoided

3. **Dual Logging Strategy**
   - **Python `logging`**: Development, debugging, CI logs (stdout)
   - **`IntegrationLog`**: Production logs visible in OneVizion UI
   - Both provide maximum observability

4. **Type Safety First**
   - All functions have type hints (strict mypy compliance)
   - `from __future__ import annotations` enables forward references
   - `TYPE_CHECKING` guards avoid runtime import costs
   - IDE support improves and bugs are caught at development time

### File Structure

```
module-template/
├── module.py              # Core business logic (Module class)
├── start_module.py        # Entry point (dependency install + orchestration)
├── settings.json          # Runtime configuration (user-provided)
├── settings_schema.json   # JSON schema for validation
├── pyproject.toml         # Modern Python project config (uv + ruff)
├── .gitignore            # Python, uv, pytest, OS artifacts
├── README.md             # Setup and usage documentation
├── CONTRIBUTING.md       # Development workflow guide
├── CLAUDE.md             # This file - context for Claude Code
├── tests/
│   ├── conftest.py       # Pytest fixtures
│   ├── test_module.py    # Unit tests for Module class
│   └── test_start_module.py  # Integration tests
├── .github/
│   └── workflows/
│       └── ci.yml        # Lint, typecheck, test pipeline
└── installation/         # OneVizion installation artifacts
    └── uninstallation/   # Cleanup scripts
```

### Key Files

#### `module.py` - Business Logic
- Contains the `Module` class with `start()` method
- **API contract must be preserved**: Other code depends on `Module(ov_module_log, settings_data)`
- Business logic goes here, kept pure and testable
- `self._module_log.add(LogLevel.INFO, "message")` sends logs to iHub
- `logger.info()` sends logs to development/CI

#### `start_module.py` - Entry Point
- **Three key functions**:
  - `install_dependencies()`: Handles package installation (uv → pip fallback)
  - `load_json_file()`: Safe JSON file loading with UTF-8
  - `validate_settings()`: JSON schema validation
  - `main()`: Orchestrates everything
- Reads three files: `settings.json`, `settings_schema.json`, `ihub_parameters.json`
- **Important**: Exits cleanly if new packages are installed (iHub reruns module)

#### `pyproject.toml` - Modern Configuration
- **Dependencies**: `jsonschema`, `onevizion` (runtime)
- **Dev dependencies**: `pytest`, `pytest-cov`, `ruff`, `mypy`
- **Ruff**: 14 rule categories enabled (strict, opinionated)
- **Mypy**: Strict mode catches type errors
- **Pytest**: 80% coverage required

## Development Workflow

### Making Changes

1. **Read existing code first**
   - Understand patterns before modifying
   - Preserve core functionality and API contracts

2. **Follow existing patterns**
   - Type hints on all functions
   - Google-style docstrings
   - Context managers for file I/O (`with open(...)`)
   - Specific exception types (never bare `except:`)

3. **Test changes**
   ```bash
   pytest -v                    # Run tests
   ruff check .                 # Lint
   ruff format .                # Format
   mypy .                       # Type check
   ```

4. **Update tests**
   - Add tests for new functionality
   - Maintain >80% coverage
   - Use fixtures from `tests/conftest.py`

### Git Workflow

- **Always work on feature branches** (never commit directly to `master`)
- Branch naming: Use Jira ticket IDs (e.g., `API-270266`, `VizionHub-12345`)
- Commit messages: Clear, specific, prefixed with type
  - `feat: add user authentication`
  - `fix: handle missing ihub_parameters.json`
  - `refactor: extract settings validation`
  - `test: add coverage for error paths`
- Push to origin and create PRs for review

### Code Quality Standards

#### Type Hints (Required)
```python
# Good
def load_json_file(path: Path) -> dict[str, Any]:
    ...

# Bad - no type hints
def load_json_file(path):
    ...
```

#### Docstrings (Required for public APIs)
```python
def validate_settings(settings_data: dict[str, Any], schema: dict[str, Any]) -> None:
    """Validate settings data against a JSON schema.

    Args:
        settings_data: The settings dictionary to validate.
        schema: The JSON schema dictionary.

    Raises:
        ValueError: If validation fails, with diagnostic message.
    """
```

#### File I/O (Use context managers)
```python
# Good
with Path("settings.json").open(encoding="utf-8") as f:
    data = json.load(f)

# Bad - manual file handling
f = open("settings.json", "rb")
data = json.loads(f.read().decode("utf-8"))
f.close()
```

#### Error Handling (Specific exceptions)
```python
# Good
try:
    validate(instance=settings_data, schema=schema)
except ValidationError as e:
    raise ValueError(f"Invalid settings: {e.message}") from e

# Bad - bare except
try:
    validate(instance=settings_data, schema=schema)
except:
    raise Exception("Validation failed")
```

## OneVizion Integration Specifics

### `onevizion` Package
- **Import**: `from onevizion import IntegrationLog, LogLevel`
- **Usage**: `module_log.add(LogLevel.INFO, "message")`
- **Log Levels**: `INFO`, `WARNING`, `ERROR`
- **Visibility**: Logs appear in OneVizion iHub UI for operators

### `ihub_parameters.json`
- iHub provides this at runtime (never commit this file)
- Contains: `processId`, `logLevel`
- Used to initialize `IntegrationLog`

### `settings.json`
- User-provided configuration (module-specific)
- Validated against `settings_schema.json`
- Common fields: `ovUrl`, `ovAccessKey`, `ovSecretKey` (OneVizion API credentials)
- Structure can be flat or nested JSON

### Dependency Installation
- **Modern approach**: `uv pip install -e .` (pyproject.toml)
- **Fallback**: `pip install -e .` if uv is unavailable (older iHub environments)
- **Production modules**: Use `python_dependencies.txt` or `.ini` files (legacy)
- **This template**: Uses pyproject.toml for modern dependency management

### Integration Marker File
- **Not included by default** in this template (inactive)
- Production modules may have `.integration` or `.integration_` files
- Declares version compatibility with OneVizion (e.g., `22.6.0+`)
- Add if multi-version support is needed

## Comparison with Production Modules

This template provides significant modernization over existing production modules:

### Template Advantages
- ✅ **Type hints**: Full coverage
- ✅ **Testing**: 32 tests, 100% coverage
- ✅ **CI/CD**: Automated lint/typecheck/test
- ✅ **Documentation**: Comprehensive docstrings
- ✅ **Error handling**: Specific exceptions with chaining
- ✅ **Logging**: Dual strategy
- ✅ **Tooling**: ruff + mypy + pytest

### Differences from Production
- 📝 **Entry point**: `start_module.py` (production uses `start_integration.py`)
- 📝 **Dependencies**: `pyproject.toml` (production uses `.txt` or `.ini` files)
- 📝 **Dependency tool**: `uv` with pip fallback (production uses pip only)
- 📝 **Code structure**: OOP with DI (production uses procedural or inheritance)

### Compatibility Considerations
- **iHub version**: Template targets 24.7.0+ (verify uv support)
- **Python version**: 3.10+ required (older iHub may use 3.8+)
- **Migration**: Existing modules can adopt patterns incrementally

## Common Tasks

### Adding Integration Features
1. Add business logic to `Module.start()` in `module.py`
2. Add required settings fields to `settings_schema.json`
3. Update `settings.json` example with new fields
4. Add unit tests to `tests/test_module.py`
5. Update README with usage examples

### Adding External Dependencies
1. Add to `dependencies = [...]` in `pyproject.toml`
2. Run `uv pip install -e .` to install
3. Import and use in code
4. Update tests to cover new functionality

### Handling API Calls
```python
import requests

def start(self) -> None:
    response = requests.get(
        f"{self._settings['apiUrl']}/endpoint",
        headers={"Authorization": f"Bearer {self._settings['apiKey']}"},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    self._module_log.add(LogLevel.INFO, f"Fetched {len(data)} records")
```

### Working with Files
```python
from pathlib import Path

def process_files(self) -> None:
    data_dir = Path("data")
    for file_path in data_dir.glob("*.json"):
        with file_path.open(encoding="utf-8") as f:
            data = json.load(f)
        self._module_log.add(LogLevel.INFO, f"Processed {file_path.name}")
```

## Constraints & Boundaries

### Must Preserve
- `Module` class API: `Module(ov_module_log, settings_data)` and `.start()`
- Settings validation flow: `settings.json` + `settings_schema.json`
- Integration with `IntegrationLog` from onevizion package
- Entry point execution model: `start_module.py` → `Module.start()`

### Can Change Aggressively
- Dependency management approach (tooling, formats)
- Code style and internal structure
- Error handling patterns
- Development tooling setup
- Testing infrastructure

### Avoid
- Breaking changes to `Module` class public API
- Removing functionality without clear justification
- Over-engineering simple patterns
- Adding unnecessary abstractions

## Testing Philosophy

### Coverage Expectations
- **Minimum**: 80% coverage (enforced by pytest)
- **Target**: >90% coverage on critical paths
- **Focus**: Error handling, edge cases, integration points

### Test Structure
```python
# tests/test_module.py - Unit tests
class TestModuleStart:
    def test_logs_start_message(self, mock_integration_log):
        module = Module(mock_integration_log, {})
        module.start()
        mock_integration_log.add.assert_called_with(LogLevel.INFO, "Module is started")

# tests/test_start_module.py - Integration tests
class TestMain:
    def test_main_happy_path(self, tmp_settings_dir, monkeypatch):
        monkeypatch.chdir(tmp_settings_dir)
        main()  # Should not raise
```

### Fixtures (tests/conftest.py)
- `valid_settings`: Sample settings dict
- `valid_schema`: JSON schema dict
- `valid_ihub_params`: iHub parameters dict
- `tmp_settings_dir`: Temp directory with all JSON files
- `mock_integration_log`: MagicMock for IntegrationLog

## Troubleshooting

### "Module 'onevizion' not found"
- Run `uv pip install -e .` to install dependencies
- Or `pip install -e .` if uv is unavailable
- In production iHub, packages install at runtime

### Tests Fail After Changes
- Run `ruff format .` to fix formatting
- Run `ruff check .` to fix linting issues
- Check test output for assertion details
- Use `pytest -vv -s` for verbose output

### Type Errors from Mypy
- Add missing type hints
- Use `Any` for complex JSON types: `dict[str, Any]`
- Add `# type: ignore[error-code]` as last resort with explanatory comment

---

# Agent Usage Guidelines

## Quick Reference

| Task Type | Recommended Agent | Why |
|-----------|------------------|-----|
| Python refactoring | `python-pro` | Expert in Python patterns, type hints, optimization |
| Adding tests | `test-automator` | Creates comprehensive test suites |
| Security review | `security-auditor` | OWASP compliance, auth flows, vulnerabilities |
| API integration | `backend-architect` | RESTful APIs, error handling, retry logic |
| Debugging issues | `debugger` | Error analysis, test failures, unexpected behavior |
| CI/CD setup | `deployment-engineer` | GitHub Actions, Docker, automation |
| Code review | `code-reviewer` | Quality, maintainability, best practices |

## Specialized Agents

### python-pro (PRIMARY AGENT)

**Use for:**
- Refactoring Python code for better idioms
- Adding or improving type hints
- Performance optimization
- Implementing Python design patterns
- Working with decorators, generators, async/await
- Modernizing legacy Python code

**Example:**
```
"Use python-pro to refactor module.py with better error handling"
```

### test-automator

**Use for:**
- Creating new test files
- Expanding test coverage to meet 80%+ requirement
- Setting up test fixtures
- Adding edge case tests
- Creating integration tests

**Note:** Maintains pytest fixtures in `tests/conftest.py` and enforces 80% coverage.

### security-auditor

**Use for:**
- Adding authentication/authorization logic
- Reviewing API key handling
- Checking for security vulnerabilities (OWASP top 10)
- Implementing secure file handling
- Validating input sanitization

**Critical:** `settings.json` contains credentials; integration modules often handle sensitive data.

### backend-architect

**Use for:**
- Designing API integration patterns
- Adding HTTP clients with retry logic
- Implementing rate limiting
- Designing error handling strategies
- Creating scalable module architecture

**Relevant:** Most OneVizion modules integrate with external APIs.

### debugger

**Use for:**
- Test failures that are hard to diagnose
- Unexpected behavior in production
- Runtime errors or exceptions
- Performance issues
- Integration problems with OneVizion iHub

### deployment-engineer

**Use for:**
- Modifying `.github/workflows/ci.yml`
- Adding new CI/CD steps
- Setting up deployment pipelines
- Optimizing build times

**Current CI:** Three jobs (lint, typecheck, test) on Python 3.10-3.13.

### code-reviewer

**Use for:**
- Proactive code review after making changes
- Before creating pull requests
- Quality checks on refactored code

## Multi-Agent Workflows

### Refactoring Workflow
1. **python-pro**: Refactor code with modern patterns
2. **test-automator**: Update tests to cover new code paths
3. **code-reviewer**: Review refactored code for quality
4. **debugger**: Fix any issues found during review

### New Feature Workflow
1. **backend-architect**: Design feature architecture
2. **python-pro**: Implement feature with type hints
3. **security-auditor**: Review for security issues
4. **test-automator**: Create comprehensive tests
5. **code-reviewer**: Final quality check

### Bug Fix Workflow
1. **debugger**: Diagnose root cause
2. **python-pro**: Implement fix
3. **test-automator**: Add regression tests
4. **code-reviewer**: Review fix for unintended side effects

## Best Practices

### Use Agents Proactively
Don't wait for user requests. If making Python changes, automatically use python-pro. If adding tests, use test-automator.

### Agent Chaining
For complex tasks, chain multiple agents:
```
1. python-pro: Refactor the code
2. test-automator: Add tests
3. code-reviewer: Review everything
```

### Provide Context
When invoking agents, include relevant context about the specific task and constraints.

### Review Agent Output
After an agent completes:
- Verify changes align with project patterns
- Check code quality standards are maintained
- Run tests to ensure nothing broke
- Review git diff before committing

## Project-Specific Agent Considerations

### OneVizion Integration Context
When using agents, always consider:
- **iHub compatibility**: Changes must work in OneVizion's environment
- **API contracts**: `Module` class interface must remain stable
- **Dual logging**: Both Python logging and IntegrationLog
- **Type safety**: Maintain strict mypy compliance
- **Test coverage**: Keep >80% coverage requirement

### Production Module Patterns
Reference `/tmp/ov-integrations-analysis/ANALYSIS.md` when:
- Comparing patterns with production modules
- Deciding whether to modernize or match existing style
- Understanding real-world usage patterns

---

## References

- **OneVizion API Docs**: Contact OneVizion for integration documentation
- **Production Module Analysis**: `/tmp/ov-integrations-analysis/ANALYSIS.md`
- **Python Best Practices**: PEP 8, PEP 484 (type hints), PEP 257 (docstrings)
- **uv Documentation**: https://github.com/astral-sh/uv
- **ruff Documentation**: https://docs.astral.sh/ruff/

**Last Updated**: 2026-05-12
**Template Version**: 1.0.0
