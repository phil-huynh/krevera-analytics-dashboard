"""
Alembic migration environment configuration.

This file is loaded when running Alembic commands and configures
how migrations are generated and applied.
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import settings to get database URL
from app.core.config import settings

# Import Base and all models so Alembic can detect them
from app.core.database import Base
from app.models import Product, MachineState, Defect

# this is the Alembic Config object
config = context.config

# Override sqlalchemy.url with environment variable if set
if settings.DATABASE_URL:
    config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate
    a connection with the context.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()