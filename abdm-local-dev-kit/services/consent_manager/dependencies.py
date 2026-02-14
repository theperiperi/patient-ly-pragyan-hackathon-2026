"""
Dependencies for FastAPI dependency injection.
"""

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase

# Global database connection
db: AsyncIOMotorDatabase = None


def set_database(database: AsyncIOMotorDatabase):
    """Set the global database connection."""
    global db
    db = database


def get_database():
    """
    Dependency to get database connection.
    """
    global db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return db
