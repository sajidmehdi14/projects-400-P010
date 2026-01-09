"""
Item service - Business logic for item operations
"""
from fastapi import HTTPException, status

from app.models.item import ItemDB, ItemCreate, ItemUpdate, ItemResponse
from app.repositories.item_repository import ItemRepository


class ItemService:
    """Service for item business logic"""

    def __init__(self, repository: ItemRepository):
        self.repository = repository

    def get_item(self, item_id: int) -> ItemResponse:
        """Get item by ID"""
        item = self.repository.get(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
            )
        return ItemResponse.model_validate(item)

    def get_items(self, skip: int = 0, limit: int = 100) -> list[ItemResponse]:
        """Get all items"""
        items = self.repository.get_all(skip=skip, limit=limit)
        return [ItemResponse.model_validate(item) for item in items]

    def get_items_by_owner(
        self, owner_id: int, skip: int = 0, limit: int = 100
    ) -> list[ItemResponse]:
        """Get items by owner"""
        items = self.repository.get_by_owner(owner_id, skip=skip, limit=limit)
        return [ItemResponse.model_validate(item) for item in items]

    def get_available_items(self, skip: int = 0, limit: int = 100) -> list[ItemResponse]:
        """Get available items"""
        items = self.repository.get_available_items(skip=skip, limit=limit)
        return [ItemResponse.model_validate(item) for item in items]

    def search_items(self, title: str, skip: int = 0, limit: int = 100) -> list[ItemResponse]:
        """Search items by title"""
        items = self.repository.search_by_title(title, skip=skip, limit=limit)
        return [ItemResponse.model_validate(item) for item in items]

    def create_item(self, item_data: ItemCreate, owner_id: int) -> ItemResponse:
        """Create a new item"""
        # Validate price
        if item_data.price < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Price cannot be negative"
            )

        # Create item
        item = ItemDB(
            title=item_data.title,
            description=item_data.description,
            price=item_data.price,
            owner_id=owner_id,
        )

        created_item = self.repository.create(item)
        return ItemResponse.model_validate(created_item)

    def update_item(self, item_id: int, item_data: ItemUpdate) -> ItemResponse:
        """Update item"""
        item = self.repository.get(item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
            )

        # Update fields if provided
        if item_data.title is not None:
            item.title = item_data.title

        if item_data.description is not None:
            item.description = item_data.description

        if item_data.price is not None:
            if item_data.price < 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Price cannot be negative",
                )
            item.price = item_data.price

        if item_data.is_available is not None:
            item.is_available = item_data.is_available

        updated_item = self.repository.update(item)
        return ItemResponse.model_validate(updated_item)

    def delete_item(self, item_id: int) -> dict:
        """Delete item"""
        if not self.repository.exists(item_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
            )

        self.repository.delete(item_id)
        return {"message": "Item deleted successfully"}
