# Coding Standards

Pi Zero 2W Medicine Tracker System - Development Guidelines

## Table of Contents

1. [Python Style Guide](#python-style-guide)
2. [Code Organization](#code-organization)
3. [Type Hints](#type-hints)
4. [Documentation](#documentation)
5. [Error Handling](#error-handling)
6. [Testing](#testing)
7. [Code Review Checklist](#code-review-checklist)

## Python Style Guide

### PEP 8 Compliance with Extensions

We follow PEP 8 with the following modifications:

#### Line Length
- **Standard:** 99 characters (extended from PEP 8's 79)
- **Rationale:** Provides better readability while maintaining portability
- **Configuration:** See `.flake8` file

```python
# Good - 99 character limit
long_variable_name = calculate_result(param1, param2, param3)

# Bad - exceeds 99 characters
long_variable_name = calculate_result(very_long_parameter_name_one, very_long_parameter_name_two, very_long_parameter_name_three)
```

#### Import Organization

Follow this order:
1. Standard library imports
2. Third-party imports
3. Local imports

Use absolute imports, not relative imports.

```python
# Good
import os
import sys
from typing import List, Optional

from flask import Flask, jsonify
from PIL import Image

from .models import User
from api.config import DATABASE_URL

# Bad
from . import models
import models  # relative import
```

#### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES = 3` |
| Functions | lower_snake_case | `def get_user_count()` |
| Classes | PascalCase | `class MedicineDatabase` |
| Variables | lower_snake_case | `user_count = 42` |
| Private | _lower_snake_case | `def _internal_helper()` |

```python
# Good
MAX_RETRY_ATTEMPTS = 5
CACHE_TTL_SECONDS = 3600

def process_medicine_data(data: dict) -> bool:
    """Process medicine tracking data."""
    pass

class MedicineTracker:
    """Tracks medicine administration."""
    pass

# Bad
max_retry_attempts = 5  # Should be UPPER_CASE
ProcessMedicineData = None  # Should be lower_snake_case
```

### Whitespace

```python
# Good - proper spacing
result = value1 + value2
dictionary = {"key": "value", "another": "item"}
func(arg1, arg2)

# Bad - improper spacing
result=value1+value2
dictionary={"key":"value","another":"item"}
func(arg1,arg2)
```

## Code Organization

### Module Structure

```
module/
├── __init__.py          # Package initialization
├── core.py              # Core functionality
├── utils.py             # Helper utilities
├── exceptions.py        # Custom exceptions
└── config.py            # Configuration
```

### File Organization Within Modules

```python
"""Module docstring."""

# 1. Standard library imports
import os
import sys

# 2. Third-party imports
from flask import Flask

# 3. Local imports
from api.config import DATABASE_URL

# 4. Constants
MAX_TIMEOUT = 30
DEFAULT_ENCODING = 'utf-8'

# 5. Exceptions
class MedicineError(Exception):
    """Base exception for medicine module."""
    pass

# 6. Classes
class Medicine:
    """Represents a medicine."""
    pass

# 7. Functions
def get_medicine(id: int) -> Optional[Medicine]:
    """Get medicine by ID."""
    pass

# 8. Main execution
if __name__ == '__main__':
    main()
```

### Class Organization

```python
class Medicine:
    """Manages medicine information."""

    # Class variables
    _cache = {}

    def __init__(self, name: str, dosage: str):
        """Initialize medicine.

        Args:
            name: Medicine name
            dosage: Dosage amount
        """
        self.name = name
        self.dosage = dosage

    # Public methods
    def administer(self) -> bool:
        """Administer this medicine."""
        pass

    # Property methods
    @property
    def is_valid(self) -> bool:
        """Check if medicine is valid."""
        return self.name is not None

    # Private methods
    def _validate_dosage(self) -> bool:
        """Validate dosage format."""
        pass

    # Dunder methods
    def __repr__(self) -> str:
        """String representation."""
        return f"Medicine({self.name})"
```

## Type Hints

### Requirements

- **Public functions:** Must have type hints
- **Public classes:** Must have type hints
- **Parameters:** All parameters should have type hints
- **Return values:** Must specify return type (use `None` for procedures)

### Type Hint Examples

```python
# Good - complete type hints
from typing import List, Optional, Dict, Tuple

def get_medicines(limit: int = 10) -> List[Medicine]:
    """Get list of medicines."""
    pass

def find_medicine(name: str) -> Optional[Medicine]:
    """Find medicine by name, return None if not found."""
    pass

def create_medicine(name: str, dosage: str) -> Tuple[bool, str]:
    """Create medicine, return (success, message) tuple."""
    pass

def get_medicine_dict() -> Dict[str, Medicine]:
    """Get medicines as dictionary."""
    pass

# Good - using Protocol for complex types
from typing import Protocol

class Drawable(Protocol):
    """Objects that can be drawn."""

    def draw(self) -> None:
        """Draw the object."""
        ...

def render(obj: Drawable) -> None:
    """Render any drawable object."""
    pass

# Bad - missing type hints
def process_data(data):  # Missing parameter and return type
    return transform(data)

def get_value(key):  # No type hints
    return cache[key]
```

### Common Type Patterns

```python
# Optional values
user: Optional[User] = None

# Lists and collections
items: List[str] = []
mapping: Dict[str, int] = {}
pair: Tuple[int, int] = (0, 0)

# Callables
callback: Callable[[int], bool] = lambda x: x > 0
handler: Callable[..., None] = setup

# Union types (multiple possible types)
value: Union[int, str] = 42

# Generics
def get_item(items: List[T]) -> T: ...
```

## Documentation

### Docstring Format

Use Google-style docstrings for all public functions and classes:

```python
def process_medicine_data(data: Dict[str, Any]) -> bool:
    """Process medicine tracking data and store in database.

    Validates the input data, transforms it to internal format,
    and stores in the database with proper error handling.

    Args:
        data: Dictionary containing medicine information with keys:
            - name: Medicine name (str)
            - dosage: Dosage amount (str)
            - frequency: How often to take (str)

    Returns:
        True if processing succeeded, False otherwise

    Raises:
        ValueError: If required fields are missing
        DatabaseError: If database operation fails

    Example:
        >>> data = {'name': 'Aspirin', 'dosage': '500mg', 'frequency': 'Daily'}
        >>> process_medicine_data(data)
        True
    """
    pass

class MedicineTracker:
    """Manages medicine tracking and administration.

    Handles recording when medicines are taken, calculating next doses,
    and generating reports on medicine adherence.

    Attributes:
        database: Database connection
        cache: In-memory cache of medicines
        last_sync: Timestamp of last database sync

    Example:
        >>> tracker = MedicineTracker(db_path='/data/medicines.db')
        >>> tracker.record_dose('aspirin', datetime.now())
        True
    """

    def __init__(self, db_path: str):
        """Initialize tracker with database path."""
        pass
```

### Module Docstrings

Every module should have a docstring at the top:

```python
"""Medicine Database Management Module

Provides SQLite-based storage and retrieval of medicine information.
Handles CRUD operations with proper transaction management and error handling.

Classes:
    MedicineDatabase: Main database interface

Functions:
    create_database(): Initialize database schema

Performance:
    - Database queries: < 10ms typical
    - Cache hit rate: > 95% for repeated queries
"""
```

### Inline Comments

- Use sparingly - code should be self-documenting
- Explain **why**, not **what**
- Keep comments up-to-date with code changes

```python
# Good - explains intent
if medicine.last_taken < now - timedelta(hours=8):
    # Medicine is overdue (should be taken every 8 hours)
    notify_user(medicine)

# Bad - redundant, restates code
count = count + 1  # Increment count
if x > 5:  # Check if x is greater than 5
    process(x)
```

## Error Handling

### Exception Hierarchy

```python
class MedicineTrackerError(Exception):
    """Base exception for medicine tracker."""
    pass

class DatabaseError(MedicineTrackerError):
    """Database operation failed."""
    pass

class ValidationError(MedicineTrackerError):
    """Data validation failed."""
    pass

class ConfigError(MedicineTrackerError):
    """Configuration error."""
    pass
```

### Proper Exception Handling

```python
# Good - specific exceptions with context
try:
    medicine = database.get_medicine(id)
except DatabaseError as e:
    logger.error("Failed to retrieve medicine: %s", e)
    raise MedicineError(f"Cannot load medicine {id}") from e

# Good - cleanup with finally
try:
    connection = database.connect()
    perform_operation(connection)
except DatabaseError as e:
    logger.error("Database operation failed: %s", e)
finally:
    connection.close()

# Good - context manager
with database.transaction():
    save_medicine(medicine)
    update_schedule(medicine)

# Bad - bare except
try:
    process_data()
except:  # Catches everything including KeyboardInterrupt
    pass

# Bad - catching too broadly
try:
    parse_json(data)
except Exception:  # Too broad
    return None
```

### Logging Standards

Use lazy formatting with `%` style:

```python
# Good - lazy evaluation
logger.info("Processing medicine %s with dosage %s", name, dosage)
logger.error("Database error: %s", error, exc_info=True)

# Bad - f-string evaluation (always evaluates)
logger.info(f"Processing medicine {name} with dosage {dosage}")

# Bad - string concatenation
logger.error("Error: " + str(error))
```

### Logging Levels

| Level | Use Case | Example |
|-------|----------|---------|
| DEBUG | Detailed diagnostic info | Variable values, function entry/exit |
| INFO | General informational messages | "App started", "User logged in" |
| WARNING | Warning conditions | "Deprecated function", "Missing optional data" |
| ERROR | Error conditions | "Database connection failed", "Invalid input" |
| CRITICAL | Critical error conditions | "Database corrupted", "System shutting down" |

## Testing

### Test File Organization

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_medicine_db.py      # Tests for medicine_db module
├── test_api.py              # Tests for API
└── api/
    ├── conftest.py          # API-specific fixtures
    └── test_endpoints.py    # Endpoint tests
```

### Test Naming Conventions

- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<function_name>_<scenario>`

```python
def test_get_medicine_returns_medicine_object():
    """Test that get_medicine returns a Medicine object."""
    pass

def test_get_medicine_raises_error_for_invalid_id():
    """Test that get_medicine raises error for invalid ID."""
    pass

class TestMedicineDatabase:
    """Tests for MedicineDatabase class."""

    def test_create_connects_to_database(self):
        """Test that create() establishes database connection."""
        pass
```

### Test Guidelines

- One assertion per test when possible
- Use descriptive test names
- Set up fixtures with clear dependencies
- Clean up after tests

```python
import pytest
from medicine_app import MedicineDatabase

@pytest.fixture
def db():
    """Create in-memory database for testing."""
    db = MedicineDatabase(":memory:")
    yield db
    db.close()

def test_add_medicine_increases_count(db):
    """Test that adding medicine increases medicine count."""
    initial_count = len(db.get_all_medicines())
    db.add_medicine("Aspirin", "500mg")
    final_count = len(db.get_all_medicines())
    assert final_count == initial_count + 1
```

## Code Review Checklist

Before submitting code for review, ensure:

### Style & Format
- [ ] Code follows PEP 8 with our extensions (99 char lines)
- [ ] Imports are properly organized
- [ ] No trailing whitespace
- [ ] Files end with newline

### Type Safety
- [ ] All public functions have type hints
- [ ] All parameters are typed
- [ ] Return types are specified
- [ ] Complex types use proper annotations

### Documentation
- [ ] Module has docstring
- [ ] All public functions/classes have docstrings
- [ ] Docstrings include Args, Returns, Raises sections
- [ ] Complex logic has explanatory comments

### Error Handling
- [ ] No bare except clauses
- [ ] Exceptions are specific
- [ ] Errors are logged with context
- [ ] Cleanup code uses finally or context managers

### Testing
- [ ] New functionality has tests
- [ ] Tests are named descriptively
- [ ] Tests pass locally
- [ ] Test coverage for edge cases

### Performance
- [ ] No N+1 query patterns
- [ ] Appropriate caching used
- [ ] Large operations are async if needed
- [ ] No memory leaks

### Linting
```bash
# Ensure all checks pass
pylint --rcfile=.pylintrc display/ api/ shared/ db/
flake8 --config=.flake8 display/ api/ shared/ db/
pytest  # Run all tests
```

## Quick Reference

### Common Patterns

#### Using Optional
```python
from typing import Optional

def get_user(id: int) -> Optional[User]:
    """Get user by ID, return None if not found."""
    user = database.find(id)
    return user if user else None
```

#### Context Managers
```python
from contextlib import contextmanager

@contextmanager
def get_database():
    """Get database connection with automatic cleanup."""
    db = connect()
    try:
        yield db
    finally:
        db.close()

# Usage
with get_database() as db:
    data = db.query()
```

#### Decorators for Logging
```python
import functools
import logging

logger = logging.getLogger(__name__)

def log_calls(func):
    """Log function calls and results."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug("Calling %s with args=%s, kwargs=%s",
                     func.__name__, args, kwargs)
        result = func(*args, **kwargs)
        logger.debug("%s returned %s", func.__name__, result)
        return result
    return wrapper

@log_calls
def process_data(data):
    return data
```

## Enforcement

### Pre-commit Hook

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash
pylint --rcfile=.pylintrc display/ api/ shared/ db/
flake8 --config=.flake8 display/ api/ shared/ db/
pytest
```

### CI/CD Integration

All code must pass these checks before merging:
1. Pylint score ≥ 9.0/10
2. Flake8 has 0 critical issues
3. All tests pass
4. Test coverage > 80%

## Questions?

Refer to:
- `.pylintrc` - Pylint configuration
- `.flake8` - Flake8 configuration
- `docs/CODE_QUALITY_REPORT.md` - Detailed quality metrics
- PEP 8 - https://www.python.org/dev/peps/pep-0008/
- Google Python Style Guide - https://google.github.io/styleguide/pyguide.html

---

Last updated: 2024-11-08
