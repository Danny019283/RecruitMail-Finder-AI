import os
from dotenv import load_dotenv
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

# Load environment variables from the .env file located in the same directory
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

# Using asyncpg driver for async PostgreSQL connection
# Make sure DATABASE_URL is defined in your .env file
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set in the .env file")

# Create the async engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create a configured "Session" class
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting an async database session.
    Use this in FastAPI routes via Depends(get_db).
    """
    async with async_session_maker() as session:
        yield session


async def init_db() -> None:
    """
    Initialize the database and create tables.
    Call this on application startup (e.g. lifespan context manager).
    """
    # Import models here so SQLModel registers them before creating tables
    from .models import Contact, Company  # noqa: F401

    async with engine.begin() as conn:
        # Create all tables registered with SQLModel
        await conn.run_sync(SQLModel.metadata.create_all)


async def recreate_db() -> None:
    """
    Drop and recreate all tables registered with SQLModel.
    Destructive: deletes any existing data. Intended for early-stage
    development migrations, not for use against a database with real data.
    """
    # Import models here so SQLModel registers them before dropping/creating tables
    from .models import Contact, Company  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
