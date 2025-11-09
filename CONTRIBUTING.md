# Contributing to Pi Zero 2W Application Suite

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Be respectful, inclusive, and professional. Treat all contributors with courtesy and respect diverse perspectives.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- Git
- Basic understanding of Python and Flask
- Familiarity with e-ink display concepts (helpful but not required)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/pizerowgpio.git
   cd pizerowgpio
   ```
3. Add upstream remote:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/pizerowgpio.git
   ```

### Set Up Development Environment

1. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Workflow

### Creating a Feature Branch

1. Update your local repository:
   ```bash
   git checkout main
   git pull upstream main
   ```

2. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

   Branch naming conventions:
   - Feature: `feature/feature-name`
   - Bug fix: `bugfix/bug-description`
   - Documentation: `docs/doc-name`
   - Refactoring: `refactor/component-name`

### Making Changes

#### Code Style

This project follows **PEP 8** with some modifications:

- **Line length:** 100 characters (not 79)
- **String quotes:** Use double quotes (`"`) for strings
- **Imports:** Use `isort` for organization
- **Formatting:** Use `black` for automatic formatting

**Run code quality tools:**
```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .

# Type checking
mypy .
```

#### Writing Code

1. **Follow project structure:**
   - Display components go in `display/`
   - API endpoints go in `api/v1/`
   - Applications go in root directory as `*_app.py`
   - Tests mirror the source structure in `tests/`

2. **Add docstrings:**
   ```python
   def process_medicine_data(data: Dict) -> List[Dict]:
       """
       Process and validate medicine data.

       Args:
           data: Raw medicine data dictionary

       Returns:
           Processed medicine list with timestamps

       Raises:
           ValueError: If required fields are missing
       """
       ...
   ```

3. **Type hints:**
   ```python
   from typing import Dict, List, Optional

   def update_config(section: str, values: Dict[str, Any]) -> bool:
       """Update configuration section."""
       ...
   ```

#### Writing Tests

All new features must include tests. Place tests in `tests/` mirroring the source structure.

**Example test:**
```python
import pytest
from medicine_app import load_medicine_data, get_pending_medicines

class TestMedicineApp:
    """Test suite for medicine application."""

    @pytest.fixture
    def sample_data(self):
        """Provide sample medicine data."""
        return {
            "medicines": [
                {
                    "id": "test_001",
                    "name": "Aspirin",
                    "dosage": "81mg",
                    "time_window": "morning",
                    "window_start": "06:00",
                    "window_end": "10:00",
                    "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
                    "active": True,
                    "pills_remaining": 30,
                    "pills_per_dose": 1,
                }
            ]
        }

    def test_load_medicine_data(self):
        """Test loading medicine data."""
        data = load_medicine_data()
        assert isinstance(data, dict)
        assert "medicines" in data

    def test_get_pending_medicines(self, sample_data):
        """Test getting pending medicines."""
        pending = get_pending_medicines(sample_data)
        assert isinstance(pending, list)

    @pytest.mark.parametrize("hour", [7, 8, 9, 10])
    def test_morning_window(self, sample_data, hour):
        """Test morning time window."""
        # Test at various hours
        pending = get_pending_medicines(sample_data, time_hour=hour)
        assert len(pending) > 0
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_medicine_app.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/unit/test_medicine_app.py::TestMedicineApp::test_load_medicine_data

# Watch mode (requires pytest-watch)
ptw
```

**Code coverage targets:**
- Target: 80%+ coverage
- Critical paths: 95%+ coverage
- Display components: 90%+ coverage

## Commit Guidelines

### Commit Messages

Follow the conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Build process, dependencies, etc.

**Examples:**
```
feat(medicine): add low-stock alert notifications

Implement email and SMS notifications when medicine stock falls below threshold.
Adds new endpoints and configuration options for notification settings.

Fixes #123

feat(display): refactor component rendering system
fix(api): resolve database connection timeout
docs(readme): update installation instructions
test(pomodoro): add timer accuracy tests
```

### Commit Best Practices

- Make atomic commits (one logical change per commit)
- Write descriptive commit messages
- Reference issues with `Fixes #123` or `Closes #456`
- Don't commit IDE settings or local configuration files

## Submitting Changes

### Before Pushing

1. **Update with upstream:**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run full test suite:**
   ```bash
   pytest
   ```

3. **Check code quality:**
   ```bash
   black .
   flake8 .
   mypy .
   ```

4. **Verify no merge conflicts:**
   ```bash
   git status
   ```

### Push and Create Pull Request

1. Push your branch:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Create a Pull Request on GitHub with:
   - Clear title describing the change
   - Description of what and why (reference issues if applicable)
   - Testing instructions if applicable
   - Screenshots/GIFs for UI changes

**Pull Request Template:**
```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix (fixes issue #123)
- [ ] New feature (implements #456)
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] Display tested on actual hardware (if applicable)

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass locally
- [ ] No new warnings generated
```

## Review Process

### Code Review

- Maintainers will review your PR within 1-3 days
- Provide constructive feedback on code, design, and tests
- Respond to reviews promptly
- Request re-review after making changes

### Approval and Merge

- Requires at least one approval from a maintainer
- All tests must pass
- Code coverage must not decrease
- No unresolved conversations

## Project Structure Guidelines

### Adding a New Application

1. Create `your_app.py` in root directory
2. Implement required interface:
   ```python
   class YourApp:
       def __init__(self, config):
           self.config = config

       def run(self):
           """Main app loop."""
           pass

       def handle_input(self, button_press):
           """Handle button input."""
           pass
   ```

3. Register in menu configuration: `config/config.json`
4. Add tests in `tests/unit/test_your_app.py`
5. Update `README.md` with app documentation

### Adding Display Components

1. Create component in `display/components.py` or new file
2. Follow existing component patterns
3. Add unit tests in `tests/unit/test_display_components.py`
4. Document usage with examples
5. Test on actual hardware with various screen sizes

### Adding API Endpoints

1. Create endpoint in `api/v1/` directory
2. Follow REST conventions
3. Add request validation
4. Add error handling
5. Document in `API_DOCUMENTATION.md`
6. Add integration tests

## Documentation

### Requirements

- All public functions must have docstrings
- Complex logic must be commented
- User-facing features must be documented in `/docs`

### Documentation Format

Use Google-style docstrings:

```python
def fetch_medicine_reminders(date: str, time_window: Optional[str] = None) -> List[Dict]:
    """
    Fetch medicine reminders for a given date.

    Queries the medicine database for active medicines due within the specified
    date and optional time window. Returns sorted by time window.

    Args:
        date: Date in YYYY-MM-DD format
        time_window: Optional window filter (morning, afternoon, evening, night)

    Returns:
        List of medicine dictionaries with reminder details:
        - medicine_id: Unique medicine identifier
        - name: Medicine name
        - dosage: Dosage string
        - time_window: Time window (morning, afternoon, evening, night)
        - window_start: Window start time (HH:MM)
        - window_end: Window end time (HH:MM)

    Raises:
        ValueError: If date format is invalid
        DatabaseError: If database query fails
    """
    ...
```

## Performance Considerations

### Display Updates

- Use partial refresh when possible (faster)
- Batch multiple small updates into one refresh
- Avoid unnecessary full refreshes
- Test display performance with actual hardware

### API Performance

- Use database indexes for frequent queries
- Implement caching where appropriate
- Monitor API response times
- Profile critical paths

### Memory Usage

- Pi Zero 2W has 512MB RAM - be mindful
- Avoid loading entire datasets into memory
- Use generators for large data sets
- Clean up resources properly

## Security

### Reporting Security Issues

- **DO NOT** open public issues for security vulnerabilities
- Email security concerns to maintainers privately
- Include proof of concept if possible
- Allow time for fix before public disclosure

### Security Guidelines

- Never hardcode credentials or API keys
- Use environment variables for secrets
- Validate all user input
- Sanitize data before database queries
- Keep dependencies up to date
- Use HTTPS for API endpoints

## Hardware Testing

If making changes to:
- Display rendering
- GPIO operations
- Hardware-specific code

Please test on actual Raspberry Pi Zero 2W hardware with Waveshare 2.13" display.

## Troubleshooting

### Common Issues During Development

#### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements-dev.txt
pip install -e .
```

#### Database Locked
```bash
# Remove lock files
rm db/*.db-*
```

#### Display Issues
- Verify SPI is enabled on Pi
- Check GPIO pins are not in use
- Ensure display is properly connected

#### Test Failures
```bash
# Run with verbose output
pytest -v -s

# Run specific test with debugging
pytest -v tests/unit/test_file.py::test_function --pdb
```

## Getting Help

- **Documentation:** Check `/docs` folder
- **Issues:** Search existing GitHub issues
- **Discussions:** Ask in GitHub Discussions
- **Direct Contact:** Email maintainers for complex questions

## Roadmap

Current planned features:
- [ ] Push notifications for medicine reminders
- [ ] Google Calendar integration
- [ ] Medication adherence reports
- [ ] Voice confirmation support
- [ ] Multiple dose per day support
- [ ] Barcode scanning for adding medicines
- [ ] Improved display refresh optimization

See [TODO](./TODO.md) for more details.

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md` file
- Release notes for their contributions
- Project documentation

Thank you for contributing!

---

**Last Updated:** November 8, 2025
**Maintainer:** Claude Code Assistant
