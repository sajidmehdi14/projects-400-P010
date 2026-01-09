"""
Item repository - Database operations for items
"""
from sqlalchemy.orm import Session

from app.models.item import ItemDB
from app.repositories.base_repository import BaseRepository


class ItemRepository(BaseRepository[ItemDB]):
    """Repository for item database operations"""

    def __init__(self, db: Session):
        super().__init__(ItemDB, db)

    def get_by_owner(self, owner_id: int, skip: int = 0, limit: int = 100) -> list[ItemDB]:
        """Get items by owner"""
        return (
            self.db.query(ItemDB)
            .filter(ItemDB.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_available_items(self, skip: int = 0, limit: int = 100) -> list[ItemDB]:
        """Get available items"""
        return (
            self.db.query(ItemDB)
            .filter(ItemDB.is_available == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search_by_title(self, title: str, skip: int = 0, limit: int = 100) -> list[ItemDB]:
        """Search items by title"""
        return (
            self.db.query(ItemDB)
            .filter(ItemDB.title.ilike(f"%{title}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )
