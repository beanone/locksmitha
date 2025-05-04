import asyncio
import os
import uuid

from keylin.models import Base, User
from passlib.hash import argon2
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

TEST_DB_PATH = os.path.abspath("tests/resources/test.db")
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"


async def seed():
    print(f"Seeding DB at: {TEST_DB_PATH}")
    # Remove old DB if exists
    if os.path.exists(TEST_DB_PATH):
        print("Removing old test.db...")
        os.remove(TEST_DB_PATH)
    else:
        print("No existing test.db found.")

    print("Creating async engine...")
    engine = create_async_engine(TEST_DB_URL, echo=True)
    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created.")

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    print("Opening session and adding user...")
    async with async_session() as session:
        user = User(
            id=uuid.uuid4(),
            email="testuser@example.com",
            hashed_password=argon2.hash("testpassword123"),
            is_active=True,
            is_superuser=False,
            is_verified=False,
            full_name="Integration Test User",
        )
        session.add(user)
        print("Committing user...")
        await session.commit()
        print("User committed.")
    print("Seeding complete.")


if __name__ == "__main__":
    asyncio.run(seed())
