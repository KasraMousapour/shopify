import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import (
    Collection,
    CollectionCreate,
    CollectionPublic,
    CollectionsPublic,
    CollectionUpdate,
    Message,
)

router = APIRouter(prefix="/collections", tags=["collections"])


@router.get("/", response_model=CollectionsPublic)
def read_collections(
    session: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Retrieve collections."""
    count_statement = select(func.count()).select_from(Collection)
    count = session.exec(count_statement).one()

    statement = select(Collection).offset(skip).limit(limit)
    collections = session.exec(statement).all()

    return CollectionsPublic(data=collections, count=count)


@router.get("/{handle}", response_model=CollectionPublic)
def read_collection_by_handle(
    handle: str,
    session: SessionDep,
) -> Any:
    """Get collection by handle (slug)."""
    statement = select(Collection).where(Collection.handle == handle)
    collection = session.exec(statement).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection


@router.post("/", response_model=CollectionPublic, dependencies=[Depends(get_current_active_superuser)])
def create_collection(
    *,
    session: SessionDep,
    collection_in: CollectionCreate,
) -> Any:
    """Create new collection (Admin only)."""
    existing = session.exec(select(Collection).where(Collection.handle == collection_in.handle)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Collection with this handle already exists")

    collection = Collection.model_validate(collection_in)
    session.add(collection)
    session.commit()
    session.refresh(collection)
    return collection


@router.put("/{id}", response_model=CollectionPublic, dependencies=[Depends(get_current_active_superuser)])
def update_collection(
    *,
    session: SessionDep,
    id: uuid.UUID,
    collection_in: CollectionUpdate,
) -> Any:
    """Update collection (Admin only)."""
    collection = session.get(Collection, id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    update_dict = collection_in.model_dump(exclude_unset=True)
    collection.sqlmodel_update(update_dict)
    session.add(collection)
    session.commit()
    session.refresh(collection)
    return collection


@router.delete("/{id}", response_model=Message, dependencies=[Depends(get_current_active_superuser)])
def delete_collection(
    *,
    session: SessionDep,
    id: uuid.UUID,
) -> Any:
    """Delete collection (Admin only)."""
    collection = session.get(Collection, id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    session.delete(collection)
    session.commit()
    return Message(message="Collection deleted successfully")
