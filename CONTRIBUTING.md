# Contributing to OSUC Digital Twin Project

Thank you for your interest in contributing to the OSUC Digital Twin Project! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Branch Naming Convention](#branch-naming-convention)
- [Pull Request Process](#pull-request-process)
- [Code Style and Standards](#code-style-and-standards)
- [Issue Reporting](#issue-reporting)
- [Development Setup](#development-setup)
- [Community and Communication](#community-and-communication)

## Getting Started

1. **Fork the repository** to your GitHub account
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/osuc_digital_twin.git
   cd osuc_digital_twin
   ```
3. **Add the upstream repository** as a remote:
   ```bash
   git remote add upstream https://github.com/Frezy145/osuc_digital_twin.git
   ```

## How to Contribute

### For New Contributors

1. Look for issues labeled with `good first issue` or `help wanted`
2. Comment on the issue to let others know you're working on it
3. Create a new branch for your contribution
4. Make your changes and test them
5. Submit a pull request

### Types of Contributions

- **Bug fixes**: Help us identify and fix bugs
- **Feature development**: Implement new features or enhancements
- **Documentation**: Improve documentation, README, or examples
- **Testing**: Add or improve test coverage
- **Code review**: Review pull requests from other contributors

## Branch Naming Convention

Please use descriptive branch names following this convention:

- `feature/description-of-feature` - for new features
- `bugfix/description-of-bug` - for bug fixes
- `docs/description-of-change` - for documentation updates
- `refactor/description-of-refactor` - for code refactoring
- `test/description-of-test` - for adding tests

Examples:
- `feature/digital-twin-simulation`
- `bugfix/memory-leak-in-processor`
- `docs/update-installation-guide`

## Pull Request Process

1. **Update your branch** with the latest changes from upstream:
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-branch-name
   git rebase main
   ```

2. **Ensure your code follows our standards**:
   - Write clear, readable code
   - Add comments where necessary
   - Include tests for new functionality
   - Update documentation as needed

3. **Create a Pull Request**:
   - Use our PR template (auto-populated)
   - Provide a clear title and description
   - Reference any related issues
   - Request review from maintainers

4. **Address feedback**:
   - Respond to review comments
   - Make requested changes
   - Update your PR as needed

## Code Style and Standards

- Follow PEP 8 for Python code (if applicable)
- Use meaningful variable and function names
- Write docstrings for functions and classes
- Keep functions small and focused
- Add type hints where appropriate
- Ensure all tests pass before submitting

## Issue Reporting

When reporting issues, please:

1. Use our issue templates
2. Provide a clear title and description
3. Include steps to reproduce the problem
4. Add relevant labels
5. Include system information if relevant

## Development Setup

### Prerequisites

- Python 3.8+ (if applicable)
- Git
- Any other project-specific requirements

### Installation

1. Clone the repository
2. Create a virtual environment (if applicable):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt  # If requirements.txt exists
   ```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src
```

## Community and Communication

- **Issues**: Use GitHub issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for general questions and ideas
- **Pull Requests**: Use PR comments for code-specific discussions

## Code of Conduct

This project follows a Code of Conduct. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Questions?

If you have questions about contributing, please:

1. Check existing issues and discussions
2. Create a new discussion for general questions
3. Create an issue for specific problems or feature requests

Thank you for contributing to the OSUC Digital Twin Project! 🚀