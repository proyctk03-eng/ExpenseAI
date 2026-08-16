# 🤝 Contributing to ExpenseAI

Thank you for considering contributing to ExpenseAI! We welcome all contributions, whether it's:
- 🐛 Bug reports
- 💡 Feature suggestions
- 📝 Documentation improvements
- 🔧 Code contributions

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL 15+
- Docker (optional but recommended)

### Development Setup
1. Fork the repository and clone your fork.
2. Create a virtual environment: `python -m venv venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Set up your `.env` file based on `.env.example`.
5. Run migrations: `alembic upgrade head`
6. Run the local server: `uvicorn src.main:app --reload`

### Code Style Guidelines
- **Python:** Follow PEP 8, use Black formatter (`black .`).
- **Type Hints:** All functions must have type hints.
- **Docstrings:** All major functions and classes must have docstrings.
- **Naming:** `snake_case` for variables/functions, `PascalCase` for classes.

### Testing Guidelines
- Write unit tests for all new features.
- Ensure your tests cover the new logic.
- Use pytest for testing: `pytest tests/`

### Commit Message Convention
- `feat`: Add new feature
- `fix`: Bug fix
- `docs`: Documentation update
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Add/modify tests
- `chore`: Maintenance tasks

## 🔄 Pull Request Process
1. Ensure your code passes all tests (`pytest`).
2. Update documentation if needed.
3. Create a descriptive PR title and description.
4. Link to related issues.
5. Wait for review from maintainers.
