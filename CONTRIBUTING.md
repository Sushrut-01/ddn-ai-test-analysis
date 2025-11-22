# Contributing to DDN AI Test Analysis System

Thank you for your interest in contributing! This document provides guidelines and instructions for participating in this project.

## Code of Conduct

Be respectful, inclusive, and collaborative. We value diverse perspectives and constructive feedback.

## Getting Started

### Prerequisites
- Python 3.9+
- Docker Desktop & Docker Compose
- PostgreSQL 13+
- Node.js 18+ (for dashboard)
- Git

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/Sushrut-01/ddn-ai-test-analysis.git
cd ddn-ai-test-analysis

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development tools

# Copy environment template
cp .env.example .env
# Edit .env with your credentials

# Start services
docker-compose up -d
```

## Development Workflow

### Branching Strategy

```
main (production-ready)
├── develop (integration branch)
    ├── feature/FEATURE-NAME
    ├── fix/BUG-FIX-NAME
    └── docs/DOCUMENTATION-UPDATE
```

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Make commits with clear messages**:
   ```bash
   git add <changed-files>
   git commit -m "feat: add your feature description"
   ```

3. **Keep commits atomic**: Each commit should represent one logical change.

4. **Write descriptive commit messages** following [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation
   - `style:` - Code formatting
   - `refactor:` - Code restructuring
   - `test:` - Tests
   - `chore:` - Maintenance

### Pull Request Process

1. Push your branch to GitHub:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Create a Pull Request with:
   - Clear title describing the change
   - Description of what changed and why
   - Reference to related issues (#123)
   - Screenshots for UI changes

3. Address feedback and keep the branch updated with `develop`

4. Once approved, squash and merge

## Code Standards

### Python Code
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use Black for formatting
- Use Pylint for linting

```bash
black implementation/
pylint implementation/
```

### JavaScript/TypeScript (Dashboard)
- Use ESLint configuration provided
- Format with Prettier
- Maximum line length: 100 characters

### Docstrings
- Write clear docstrings for all functions and classes
- Include parameter descriptions and return types
- Add examples for complex functions

## Testing

### Running Tests

```bash
# All tests
python -m pytest tests/

# Specific test file
python -m pytest tests/test_agent.py

# With coverage
python -m pytest --cov=implementation tests/
```

### Writing Tests
- Test coverage target: >80%
- Use descriptive test names: `test_should_<expected_behavior>_when_<condition>`
- Test both success and failure cases
- Mock external services

## Documentation

- Update README.md if changing user-facing features
- Update DEVELOPMENT.md for setup/architecture changes
- Add docstrings to code
- Include examples for new features
- Document breaking changes prominently

## Reporting Issues

Use GitHub Issues with:
- Clear, descriptive title
- Detailed description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Screenshots/logs if relevant

## Questions or Need Help?

- Check existing documentation in `/docs`
- Search closed issues for similar questions
- Create a new discussion or issue
- Contact the maintainers

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

Thank you for contributing!
