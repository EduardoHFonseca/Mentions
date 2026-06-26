# AGENTS.md

## Overview
This file provides guidelines for AI agents working in this repository.

## Build/Test/Lint Commands

### JavaScript/TypeScript (npm/pnpm)
```bash
# Development
npm run dev              # Start development server
npm run build            # Production build
npm run preview          # Preview production build

# Testing
npm test                 # Run all tests
npm test -- --watch      # Watch mode
npm test -- path/to/test # Run single test file
npm test -- -t "test name" # Run specific test

# Quality
npm run lint             # Run ESLint
npm run lint:fix         # Fix auto-fixable issues
npm run typecheck        # TypeScript type checking
npm run format           # Format with Prettier
```

### Python
```bash
# Development
python -m pip install -e .     # Install package
poetry install                  # With Poetry
uv sync                         # With uv

# Testing
pytest                         # Run all tests
pytest tests/test_file.py      # Single file
pytest -k "test_name"          # Specific test
pytest --cov=src               # With coverage

# Quality
ruff check .                  # Lint with Ruff
ruff check --fix .            # Auto-fix
black .                       # Format with Black
mypy src/                     # Type check
```

### Rust
```bash
# Development
cargo build                   # Build
cargo build --release         # Release build

# Testing
cargo test                    # Run all tests
cargo test test_name          # Specific test
cargo test --lib              # Library tests only
cargo test --doc             # Doc tests only

# Quality
cargo fmt                     # Format code
cargo clippy                  # Lint with Clippy
cargo clippy --fix           # Auto-fix
cargo check                  # Type check
```

### Go
```bash
# Development
go build ./...                # Build all packages

# Testing
go test ./...                 # Run all tests
go test -v ./...             # Verbose
go test -run TestName        # Specific test
go test -cover               # With coverage

# Quality
go fmt ./...                  # Format code
go vet ./...                  # Type check
golangci-lint run            # Lint with golangci-lint
```

---

## Code Style Guidelines

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Variables/functions | camelCase | `getUserData`, `isActive` |
| Classes/types | PascalCase | `UserService`, `ApiResponse` |
| Constants | SCREAMING_SNAKE | `MAX_RETRIES`, `API_URL` |
| Files (JS/TS) | kebab-case | `user-service.ts`, `api-utils.ts` |
| Files (Python) | snake_case | `user_service.py`, `api_utils.py` |
| Files (Rust) | snake_case | `user_service.rs`, `mod.rs` for modules |
| Files (Go) | snake_case | `user_service.go` |

### Import Organization

**JavaScript/TypeScript (ESLint/Prettier order):**
1. Node.js built-ins (`node:fs`, `node:path`)
2. External packages (`react`, `lodash`)
3. Internal modules (`@/components`, `../utils`)
4. Type imports (`type { User }`)

**Python:**
```python
# Standard library
import os
from typing import Optional

# Third-party
from fastapi import FastAPI
from pydantic import BaseModel

# Local
from . import models
from .utils import helpers
```

**Rust:**
```rust
use std::io::{self, Read};
use serde::{Deserialize, Serialize};
use crate::models::User;
```

### Formatting

- **Line length**: 100 characters max (configurable)
- **Indentation**: 4 spaces (or 2 for JS/TS projects using Prettier)
- **Semicolons**: Required (JS without Prettier), omitted (Prettier projects)
- **Trailing commas**: Required in multiline structures
- **Quotes**: Single quotes (JS/TS), double quotes (Python)
- **Braces**: K&R style (opening brace on same line)

### Type Annotations

**TypeScript:**
```typescript
// Explicit types for function parameters and returns
function processUser(user: User): Promise<Result> {
  return fetchUser(user.id);
}

// Interface over type for object shapes
interface UserProfile {
  id: string;
  name: string;
  email?: string;
}
```

**Python:**
```python
def process_user(user_id: str) -> Optional[User]:
    """Process user by ID."""
    return db.query(User).filter(User.id == user_id).first()
```

**Rust:**
```rust
fn process_user(user_id: String) -> Option<User> {
    db.query::<User>().filter(|u| u.id == user_id).first()
}
```

---

## Error Handling

### JavaScript/TypeScript
```typescript
// Use specific error classes
class ValidationError extends Error {
  constructor(message: string, public field: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

// Try-catch with async/await
try {
  const result = await api.fetchData();
} catch (error) {
  if (error instanceof ValidationError) {
    // Handle specific error
  }
  throw error; // Re-throw if not handled
}
```

### Python
```python
# Custom exceptions
class ValidationError(Exception):
    def __init__(self, message: str, field: str):
        super().__init__(message)
        self.field = field

# Handle with specific exceptions
try:
    result = api.fetch_data()
except ValidationError as e:
    logger.warning(f"Validation failed: {e.field}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

### Rust
```rust
// Use Result type
fn process_user(id: String) -> Result<User, UserError> {
    db.query::<User>()
        .filter(|u| u.id == id)
        .first()
        .map_err(|_| UserError::NotFound(id))
}

// Propagate errors with ?
let user = process_user(id)?;
```

---

## Git Workflow

### Commit Messages
Format: `<type>(<scope>): <description>`

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
- `feat(auth): add OAuth2 login`
- `fix(api): handle null response`
- `docs(readme): update installation`

### Branch Naming
- Feature: `feature/user-authentication`
- Bugfix: `fix/handle-null-values`
- Hotfix: `hotfix/security-patch`
- Release: `release/v1.2.0`

### Pull Requests
- Title: Clear description of changes
- Description: What, why, and how
- Tests: Include/update tests
- Docs: Update if needed

---

## General Best Practices

### Comments
- Use JSDoc/TSDoc for public APIs
- Explain "why", not "what"
- Keep comments updated with code changes

### Security
- Never commit secrets/credentials
- Use environment variables
- Validate all user input
- Sanitize data before display

### Performance
- Lazy load large modules
- Memoize expensive computations
- Use pagination for large datasets
- Profile before optimizing

### Testing
- Test behavior, not implementation
- Mock external dependencies
- Aim for meaningful coverage, not 100%
- Write tests before fixing bugs (TDD)

---

## Instant Hosting (here.now)

Use `here.now` to share static prototypes, files, or documentation instantly.

### Publishing
```bash
/home/efonseca/.claude/skills/here-now/scripts/publish.sh <file-or-dir>
```

- **Anonymous**: Expires in 24h (default if no API key).
- **Authenticated**: Permanent (requires `~/.herenow/credentials`).
---

## Specific Directives
- **Este projeto deve ser executado APENAS em webservice local.**
- **DIRETIVA DE TENTATIVAS:** Se houver uma tentativa de corrigir um problema de desenvolvimento mais de 5 vezes na mesma sequência sem resultado, propor outras soluções em diferentes tecnologias.
