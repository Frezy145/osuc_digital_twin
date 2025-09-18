# Development Guide

This guide provides detailed information for developers working on the OSUC Digital Twin Project.

## Table of Contents

- [Development Environment Setup](#development-environment-setup)
- [Project Architecture](#project-architecture)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Git Workflow](#git-workflow)
- [Release Process](#release-process)
- [Troubleshooting](#troubleshooting)

## Development Environment Setup

### Prerequisites

Make sure you have the following installed:

- **Git** (latest version)
- **Python 3.8+** (if applicable)
- **Node.js 16+** (if applicable)
- **Docker** (optional, for containerized development)

### IDE Recommendations

- **Visual Studio Code** with extensions:
  - Python (if applicable)
  - GitLens
  - GitHub Pull Requests and Issues
  - Black Formatter
  - isort
  - Pylint

- **PyCharm** (for Python development)
- **Cursor** (AI-powered development)

### Initial Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/osuc_digital_twin.git
   cd osuc_digital_twin
   git remote add upstream https://github.com/Frezy145/osuc_digital_twin.git
   ```

2. **Create Development Environment**
   ```bash
   # For Python projects
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install development dependencies
   pip install -r requirements-dev.txt
   ```

3. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

4. **Verify Setup**
   ```bash
   # Run tests
   python -m pytest
   
   # Run linters
   flake8 .
   black --check .
   isort --check-only .
   ```

## Project Architecture

### Directory Structure

```
osuc_digital_twin/
├── .github/                 # GitHub workflows and templates
├── src/                     # Source code
│   ├── core/               # Core functionality
│   ├── models/             # Data models
│   ├── services/           # Business logic
│   └── utils/              # Utilities
├── tests/                  # Test files
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── fixtures/           # Test data
├── docs/                   # Documentation
├── scripts/                # Build and deployment scripts
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
└── setup.py               # Package setup
```

### Coding Standards

#### Python (if applicable)

- **PEP 8** compliance
- **Type hints** for all functions
- **Docstrings** for all modules, classes, and functions
- **Maximum line length**: 88 characters (Black default)

Example:
```python
def calculate_digital_twin_parameters(
    input_data: Dict[str, Any],
    model_type: str = "default"
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate parameters for digital twin model.
    
    Args:
        input_data: Input parameters for calculation
        model_type: Type of model to use
        
    Returns:
        Tuple of calculated value and metadata
        
    Raises:
        ValueError: If input_data is invalid
    """
    # Implementation here
    pass
```

#### General Guidelines

- **Meaningful names** for variables and functions
- **Small functions** (max 20-30 lines)
- **Single responsibility** principle
- **Error handling** with appropriate exceptions
- **Logging** instead of print statements

## Testing Guidelines

### Test Structure

- **Unit tests**: Test individual functions/classes
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete workflows

### Writing Tests

```python
import pytest
from src.core.calculator import calculate_digital_twin_parameters

class TestDigitalTwinCalculator:
    def test_calculate_parameters_success(self):
        """Test successful parameter calculation."""
        input_data = {"param1": 10, "param2": 20}
        result, metadata = calculate_digital_twin_parameters(input_data)
        
        assert result > 0
        assert "timestamp" in metadata
    
    def test_calculate_parameters_invalid_input(self):
        """Test parameter calculation with invalid input."""
        with pytest.raises(ValueError):
            calculate_digital_twin_parameters({})
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_calculator.py

# Run tests with verbose output
python -m pytest -v
```

## Git Workflow

### Branch Strategy

- **main**: Production-ready code
- **develop**: Integration branch for features
- **feature/**: New features
- **bugfix/**: Bug fixes
- **hotfix/**: Critical fixes

### Workflow Steps

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/digital-twin-simulation
   ```

2. **Make Changes**
   ```bash
   # Make your changes
   git add .
   git commit -m "feat: add digital twin simulation functionality"
   ```

3. **Keep Updated**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

4. **Push and Create PR**
   ```bash
   git push origin feature/digital-twin-simulation
   # Create PR via GitHub UI
   ```

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH**
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps

1. Update version in `setup.py` or `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release branch: `git checkout -b release/v1.2.0`
4. Test thoroughly
5. Merge to main and tag: `git tag v1.2.0`
6. Create GitHub release with release notes

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Solution: Install in development mode
pip install -e .
```

#### Test Failures
```bash
# Clear pytest cache
rm -rf .pytest_cache
python -m pytest --cache-clear
```

#### Pre-commit Issues
```bash
# Update pre-commit hooks
pre-commit autoupdate
pre-commit run --all-files
```

### Getting Help

- **GitHub Discussions**: For general questions
- **Issues**: For bugs and feature requests
- **Code Review**: For specific code questions
- **Documentation**: Check existing docs first

### Performance Tips

- Use virtual environments
- Install dependencies in development mode
- Use pytest-xdist for parallel testing
- Profile code with cProfile for optimization

---

## Contributing to This Guide

This development guide is living documentation. Please contribute improvements:

1. Fork the repository
2. Edit this file
3. Submit a pull request
4. Tag maintainers for review

Thank you for helping improve our development process! 🚀