# Contributing to Google Play Reviews Explorer

Thank you for your interest in contributing to Google Play Reviews Explorer! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Python version, etc.)
- **Screenshots** if applicable
- **Error messages** or logs

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:

- Use a clear and descriptive title
- Provide a detailed description of the suggested enhancement
- Explain why this enhancement would be useful
- Include examples of how it would work

### Pull Requests

1. **Fork the repository** and create your branch from `main`:
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make your changes**:
   - Follow the coding style used throughout the project
   - Write clear, concise commit messages
   - Add or update tests as needed
   - Update documentation if needed

3. **Test your changes**:
   ```bash
   ./run_tests.sh
   ```
   Ensure all tests pass and coverage remains high.

4. **Commit your changes**:
   ```bash
   git commit -m "Add amazing feature"
   ```

5. **Push to your fork**:
   ```bash
   git push origin feature/amazing-feature
   ```

6. **Open a Pull Request** with:
   - Clear title describing the change
   - Description of what changed and why
   - Link to any related issues
   - Screenshots (if UI changes)

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip and venv
- Git

### Setting Up Development Environment

1. **Clone your fork**:
   ```bash
   git clone https://github.com/yourusername/google-reviews.git
   cd google-reviews
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your test values
   ```

5. **Run tests**:
   ```bash
   ./run_tests.sh
   ```

6. **Start the development server**:
   ```bash
   ./run.sh
   ```

## Coding Guidelines

### Python Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints where appropriate
- Write docstrings for functions and classes
- Keep functions focused and small
- Use meaningful variable names

### Code Structure

```python
"""Module docstring describing the purpose."""
from __future__ import annotations

import standard_library
import third_party

from .local_module import Something


def function_name(param: str) -> bool:
    """Function docstring.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
    """
    # Implementation
    return True
```

### Testing

- Write tests for new features
- Maintain or improve code coverage
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern
- Use fixtures for common test data

Example test:
```python
import pytest

@pytest.mark.unit
class TestMyFeature:
    """Tests for my feature."""
    
    def test_feature_works_correctly(self, mock_data):
        """Test that feature handles normal case."""
        # Arrange
        input_data = mock_data
        
        # Act
        result = my_feature(input_data)
        
        # Assert
        assert result == expected_value
```

### Commit Messages

Use clear, descriptive commit messages:

```
Add feature: brief description

Detailed explanation of what changed and why.
Include any relevant context or decisions made.

Fixes #123
```

### Documentation

- Update README.md for user-facing changes
- Update relevant docs/ files for technical changes
- Add docstrings to new functions/classes
- Include examples for new features

## Testing

### Running Tests

```bash
# All tests with coverage
./run_tests.sh

# Unit tests only
./run_tests.sh unit

# Integration tests only
./run_tests.sh integration

# Specific test file
./run_tests.sh specific tests/unit/test_schemas.py

# Fast mode (no coverage)
./run_tests.sh fast

# Verbose output
./run_tests.sh verbose
```

### Test Coverage

- Maintain at least 80% code coverage
- All new code should include tests
- Critical paths should have 100% coverage

View coverage report:
```bash
./run_tests.sh coverage
open htmlcov/index.html
```

## Project Structure

```
google-reviews/
├── app/                    # Application code
│   ├── api/               # API routes
│   ├── services/          # Business logic
│   ├── ai/                # AI/ML features
│   ├── config.py          # Configuration
│   ├── schemas.py         # Data models
│   └── main.py            # App entry point
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests
├── templates/            # HTML templates
├── static/               # CSS/JS assets
├── docs/                 # Documentation
└── sample_data/          # Mock data
```

## Adding New Features

### 1. Plan Your Feature

- Open an issue to discuss the feature
- Get feedback from maintainers
- Agree on implementation approach

### 2. Implement

- Create a feature branch
- Write the code following guidelines
- Add comprehensive tests
- Update documentation

### 3. Submit

- Ensure all tests pass
- Update CHANGELOG.md (if exists)
- Create pull request
- Respond to review feedback

## Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, a maintainer will merge
4. Your contribution will be in the next release!

## Questions?

- Open an issue for questions
- Tag it with "question" label
- Maintainers will respond as soon as possible

## Recognition

Contributors will be:
- Listed in project documentation
- Credited in release notes
- Part of our growing community!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Google Play Reviews Explorer! 🎉

