# remail

ReMail - Email management with AI-powered features

## For New Developers

### Getting Started

This project uses [Pixi](https://pixi.sh) for dependency management and task execution. Pixi provides a fast, cross-platform package manager that handles both conda and PyPI packages.

#### Prerequisites

Install Pixi:

```bash
curl -fsSL https://pixi.sh/install.sh | bash
```

#### Setup

Clone and install dependencies:

```bash
git clone https://github.com/koesterlab/remail2.git
cd remail2
pixi install
```

### Available Commands

The project includes several pixi tasks defined in `pixi.toml`:

- **`pixi run test`** - Run the test suite with pytest
- **`pixi run lint`** - Check code for linting errors with Ruff
- **`pixi run format`** - Automatically fix linting issues and format code
- **`pixi run format-check`** - Check formatting and linting without making changes (used in CI)
- **`pixi run typecheck`** - Run mypy (currently scoped to modules not excluded in `mypy.ini`)
- **`pixi run deadcode`** - Identify unused code paths with Vulture (legacy-heavy modules are excluded)
- **`pixi run security`** - Execute Bandit security scans (legacy-heavy modules are excluded)

### Development Workflow

1. Make your changes
2. Format your code: `pixi run format`
3. Run tests: `pixi run test`
4. Create a pull request

### CI/CD Workflows

The project uses GitHub Actions for automated quality checks:

#### Code Quality (`.github/workflows/code-quality.yml`)

Runs on all pull requests to `main`:

- ✅ Runs test suite
- ✅ Checks code linting
- ✅ Verifies code formatting and import organization
- ✅ Runs mypy type checks
- ✅ Executes Vulture for dead code detection
- ✅ Executes Bandit security scan

#### Auto-assign Author (`.github/workflows/auto-assign-author.yml`)

Automatically assigns pull requests to their author for tracking.

#### Dependabot Auto-merge (`.github/workflows/dependabot-auto-merge.yml`)

Automatically approves and merges Dependabot pull requests for patch and minor version updates.

### Tech Stack

- **Python 3.12+**
- **Database**: DuckDB with SQLModel ORM
- **Frontend**: Streamlit / Flet
- **AI/LLM**: LlamaIndex, ChromaDB for RAG, Hugging Face embeddings
- **Email**: IMAP and Exchange protocol support
- **Code Quality**: Ruff (linting & formatting), pytest (testing)
