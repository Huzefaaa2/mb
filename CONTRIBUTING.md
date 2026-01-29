# Contributing to Magic Bus

Thank you for your interest in contributing to the Magic Bus Youth Employment Platform! This document provides guidelines and instructions for contributing.

## Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please read our Code of Conduct carefully.

### Our Pledge

We are committed to making participation in this project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, sex characteristics, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check if the issue has already been reported in [Issues](https://github.com/magicbus/mb/issues).

When creating a bug report, include:
- **Clear description**: What is the problem?
- **Steps to reproduce**: How do you trigger the bug?
- **Expected behavior**: What should happen?
- **Actual behavior**: What actually happens?
- **Screenshots**: If applicable
- **Environment**: Python version, OS, browser
- **Additional context**: Any other relevant information

### Feature Requests

Feature requests are tracked as [GitHub Issues](https://github.com/magicbus/mb/issues/new).

When creating a feature request, include:
- **Clear title**: What feature?
- **Detailed description**: What is the feature about?
- **Use cases**: Why is this useful?
- **Proposed implementation**: How might you implement it?
- **Screenshots/mockups**: If applicable
- **Additional context**: Any other relevant information

### Pull Requests

- Fill in the required template
- Follow the styleguides
- Ensure tests pass
- Ensure documentation is updated
- Follow commit message conventions

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub

# Clone your fork
git clone https://github.com/YOUR-USERNAME/mb.git
cd mb

# Add upstream remote
git remote add upstream https://github.com/magicbus/mb.git
```

### 2. Create Feature Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
```

### 3. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv

# Activate environment
# Windows:
.\venv\Scripts\Activate.ps1
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements-py311.txt
pip install -r requirements-dev.txt  # Development dependencies

# Install pre-commit hooks
pre-commit install
```

### 4. Make Changes

- Write clean, readable code
- Follow the code style guide
- Add tests for new features
- Update documentation as needed

### 5. Test Your Changes

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_auth.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Format code
black app/ config/ scripts/

# Check imports
isort app/ config/ scripts/

# Lint code
flake8 app/ config/ scripts/
```

### 6. Commit Changes

```bash
# Stage changes
git add .

# Commit with meaningful message
git commit -m "feat: Add new feature

- Description of first change
- Description of second change

Fixes #123"
```

### 7. Push and Create PR

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
# - Fill in PR template
# - Reference related issues
# - Describe changes clearly
```

## Code Style Guide

### Python Code Style

We follow PEP 8 with some customizations:

```python
# Use type hints
def get_user_modules(user_id: int) -> list[dict]:
    """Get all modules assigned to a user.
    
    Args:
        user_id: The user's ID
        
    Returns:
        List of module dictionaries
    """
    pass

# Use descriptive names
user_modules = db.query_modules(user_id)

# Use docstrings
class UserService:
    """Service for user management operations."""
    
    def register_user(self, email: str, password: str) -> User:
        """Register a new user."""
        pass

# Use f-strings
message = f"User {user_id} created at {timestamp}"

# Limit line length to 100 characters
# Use proper spacing and indentation
```

### Naming Conventions

- **Modules**: `snake_case` (e.g., `user_service.py`)
- **Classes**: `PascalCase` (e.g., `UserService`)
- **Functions**: `snake_case` (e.g., `get_user_by_id`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_USERS`)
- **Private methods**: `_snake_case` (e.g., `_validate_input`)

### Import Organization

```python
# 1. Standard library
import os
import sys
from datetime import datetime

# 2. Third-party libraries
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

# 3. Local imports
from app.services.user_service import UserService
from config.settings import Settings
```

### Documentation

All functions should have docstrings:

```python
def calculate_sector_fit(user_data: dict) -> dict:
    """Calculate sector fit score for a user.
    
    Args:
        user_data: Dictionary containing user information
                   - 'sector_interests': list of interested sectors
                   - 'skills': list of user skills
                   - 'experience': years of experience
    
    Returns:
        Dictionary with:
        - 'sector': Best matching sector
        - 'fit_score': Score 0-100
        - 'confidence': Confidence level
        - 'recommendations': List of recommended paths
    
    Raises:
        ValueError: If user_data is missing required fields
        
    Example:
        >>> user = {'sector_interests': ['AI', 'ML'], 'skills': ['Python']}
        >>> result = calculate_sector_fit(user)
        >>> result['fit_score']
        75
    """
    pass
```

## Testing

### Writing Tests

```python
import pytest
from app.services.auth_service import AuthService

class TestAuthService:
    """Test cases for authentication service."""
    
    @pytest.fixture
    def auth_service(self):
        """Create an auth service instance for testing."""
        return AuthService()
    
    def test_register_user_success(self, auth_service):
        """Test successful user registration."""
        result = auth_service.register(
            email="test@example.com",
            password="secure_password"
        )
        
        assert result['success'] is True
        assert result['user_id'] is not None
    
    def test_register_duplicate_email(self, auth_service):
        """Test registration with duplicate email."""
        auth_service.register(
            email="test@example.com",
            password="password"
        )
        
        with pytest.raises(ValueError, match="Email already registered"):
            auth_service.register(
                email="test@example.com",
                password="different_password"
            )
    
    @pytest.mark.parametrize("email,expected", [
        ("valid@example.com", True),
        ("invalid.email", False),
        ("", False),
    ])
    def test_validate_email(self, auth_service, email, expected):
        """Test email validation."""
        result = auth_service.validate_email(email)
        assert result == expected
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::TestAuthService::test_register_user_success

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=html

# Run and stop on first failure
pytest -x

# Run last failed tests
pytest --lf
```

## Commit Message Guidelines

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type

- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that don't affect code meaning
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `perf`: Code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to build process or dependencies

### Scope

Optional, but recommended:
- `auth`: Authentication module
- `database`: Database operations
- `analytics`: Analytics features
- `survey`: Survey system
- `ui`: User interface
- `integration`: External integrations

### Subject

- Use imperative, present tense: "add" not "added" or "adds"
- Don't capitalize first letter
- No period (.) at the end
- Maximum 50 characters

### Body

- Optional but recommended for complex changes
- Explain what and why, not how
- Wrap at 72 characters
- Separate from subject with blank line

### Footer

- Reference issues: `Fixes #123` or `Closes #123`
- Breaking changes: `BREAKING CHANGE: description`

### Examples

```
feat(auth): add two-factor authentication

Add support for optional two-factor authentication:
- Implement OTP validation
- Add user setting for 2FA
- Update login flow

Fixes #42

feat(database): migrate to Azure SQL
docs(wiki): update deployment guide
fix(survey): resolve validation error on submit
style: format imports according to PEP 8
refactor(analytics): simplify risk calculation
perf(api): optimize database query performance
test(auth): add unit tests for password reset
chore(deps): upgrade streamlit to 1.20.0
```

## Review Process

1. **Automated Checks**: 
   - Code quality (Flake8, Black, isort)
   - Unit tests (pytest)
   - Security scan (Bandit)
   - Build docker image

2. **Code Review**: 
   - At least one approval required
   - Address reviewer feedback
   - Maintain conversation

3. **Merge**: 
   - Squash commits if needed
   - Delete feature branch after merge

## Additional Notes

### Getting Help

- **Documentation**: Check [docs/wiki](./docs/wiki)
- **Issues**: Search existing issues for answers
- **Discussions**: Join community discussions
- **Email**: Contact team@magicbus.org

### Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md`
- Release notes
- Project website

### License

By contributing, you agree that your contributions will be licensed under its MIT License.

---

Thank you for contributing to Magic Bus! 🎓

