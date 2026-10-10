# Hobby Tracker - Infrastructure (v0.1.0)

![Python Version](https://img.shields.io/badge/Python%20Version-3.14%2B-0969da?logo=python)
![ORM](https://img.shields.io/badge/ORM-SQLAlchemy-ffffff?logo=sqlalchemy)
![migrations](https://img.shields.io/badge/migrations-alembic-0969da)

This repository contains implementations of some core interfaces for the Hobby Tracker application.

The  project uses the core package [hobby-tracker-core](https://github.com/griy-rerere/hobby-tracker-core).

## 🎯 Features

The infrastructure package now has these sub-packages:

### Persistence(SQL Databases)

Uses [sqlalchemy](https://github.com/sqlalchemy/sqlalchemy) ORM library for implemetation of these interfaces:

* Query handlers
* Domain Repositories
* UnitOfWork

#### Table structure

```mermaid
erDiagram
    user {
        UUID id PK "Primary Key"
    }
    telegram_account {
        int telegram_id PK "Primary Key"
        UUID user_id FK "Foreign Key to user"
    }
    hobby {
        UUID id PK "Primary Key"
        string name "Not null"
        UUID user_id FK "Foreign Key to user"
    }
    activity {
        UUID id PK "Primary Key"
        UUID hobby_id FK "Foreign Key to hobby"
        datetime started_at "Not null"
        int duration_minutes "Not null"
        string note "Nullable"
    }
    user ||--o{ hobby : "owns / manages"
    user ||--o{ telegram_account: "has"
    hobby ||--o{ activity : "consists of"
```

#### Migrations

Alembic library is used to manage migrations. See [alembic](https://github.com/sqlalchemy/alembic) to check the migration process. Put these envs to your `.env` file:

| Environment Variable | meaning |
| -------------------- | ------- |
| `DATABASE_URL` | Standart **sqlalchemy** db url with format `dialect+driver://username:password@host:port/database` |

## 🛠️ Code Quality & Verification

The core domain guarantees absolute reliability through strict type safety and high test coverage.

Before committing, make sure all quality gates pass successfully:

* **Formatting & Linting (Ruff):**
  ```bash
  poetry run ruff check .
  poetry run ruff format .
  ```
* **Strict Static Typing (MyPy):**
  ```bash
  poetry run mypy hobby_tracker_infrastrucure
  ```
* **Unit Testing (PyTest):**
  ```bash
  poetry run pytest
  ```

## 📥 Local Installation & Integration

To link this core package to your presentation or infrastructure layer during development, add it to your `pyproject.toml` via Git URL:

```toml
[project]
dependencies = [
    "hobby-tracker-infrastructure @ git+https://github.com/griy-rerere/hobby-tracker-infrastructure.git"
]
```

Or install it directly via pip:
```bash
pip install git+https://github.com/griy-rerere/hobby-tracker-infrastructure.git
```

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.
