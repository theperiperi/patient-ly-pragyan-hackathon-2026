"""
Database module for HIU service.

Provides a global database connection accessible from all modules.
"""

from motor.motor_asyncio import AsyncIOMotorDatabase

# Global database connection
db: AsyncIOMotorDatabase = None


def get_database() -> AsyncIOMotorDatabase:
    """
    Get the global database connection.

    Returns:
        The database connection instance
    """
    return db


def set_database(database: AsyncIOMotorDatabase):
    """
    Set the global database connection.

    Args:
        database: The database connection to set
    """
    global db
    db = database
