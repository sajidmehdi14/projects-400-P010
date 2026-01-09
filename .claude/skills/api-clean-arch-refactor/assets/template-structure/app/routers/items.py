"""
Item router - API endpoints for items
"""
from fastapi import APIRouter, Query, status

from app.core.dependencies import ItemServiceDep
from app.models.item import ItemCreate, ItemUpdate, ItemResponse

router = APIRouter()


@router.get("/", response_model=list[ItemResponse])
def get_items(
    service: ItemServiceDep,
    skip: int = 0,
    limit: int = 100,
    available_only: bool = Query(False, description="Filter available items only"),
    search: str = Query(None, description="Search by title"),
):
    """Get all items with optional filters"""
    if search:
        return service.search_items(search, skip=skip, limit=limit)
    if available_only:
        return service.get_available_items(skip=skip, limit=limit)
    return service.get_items(skip=skip, limit=limit)


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, service: ItemServiceDep):
    """Get item by ID"""
    return service.get_item(item_id)


@router.get("/owner/{owner_id}", response_model=list[ItemResponse])
def get_items_by_owner(
    owner_id: int,
    service: ItemServiceDep,
    skip: int = 0,
    limit: int = 100,
):
    """Get items by owner"""
    return service.get_items_by_owner(owner_id, skip=skip, limit=limit)


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    item: ItemCreate,
    service: ItemServiceDep,
    owner_id: int = Query(..., description="Owner user ID"),
):
    """Create a new item"""
    return service.create_item(item, owner_id)


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemUpdate, service: ItemServiceDep):
    """Update item"""
    return service.update_item(item_id, item)


@router.delete("/{item_id}")
def delete_item(item_id: int, service: ItemServiceDep):
    """Delete item"""
    return service.delete_item(item_id)
