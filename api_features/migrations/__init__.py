"""
================================================================================
MIGRATIONS - PACKAGE INITIALIZATION
================================================================================

Package marker for Django migrations directory.

PURPOSE:
This file marks the migrations/ directory as a Python package, allowing Django
to discover and manage database schema migrations.

WHAT ARE MIGRATIONS?
Migrations are version-controlled Python files that describe changes to your
database schema. They allow you to evolve your database design over time while
keeping track of all changes.

CREATING MIGRATIONS:
  # Create migration files from model changes
  python manage.py makemigrations api_features
  
  # Apply migrations to database
  python manage.py migrate

STRUCTURE:
  migrations/
    ├── __init__.py              (This file)
    ├── 0001_initial.py          (First schema)
    ├── 0002_add_field.py        (Add a field)
    └── ...

COMMON MIGRATIONS:
  - 0001_initial.py     - Created when you first run makemigrations
  - 0002_*.py           - Subsequent changes to models

VIEWING MIGRATION STATUS:
  python manage.py showmigrations api_features

REVERTING MIGRATIONS:
  python manage.py migrate api_features 0001  # Go back to 0001
  python manage.py migrate api_features zero  # Remove all migrations

CURRENT STATUS:
No models are currently defined in models.py, so no migrations exist yet.
When database models are added, migration files will be generated here.

================================================================================
"""
