import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import col, func, select

from app.api.deps import SessionDep, get_current_active_superuser
from app.models import (
    Collection,
    Message,
    Product,
    ProductCreate,
    ProductPublic,
    ProductsPublic,
    ProductUpdate,
    ProductVariant,
    ProductVariantCreate,
    ProductVariantPublic,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=ProductsPublic)
def read_products(
    session: SessionDep,
    skip: int = 0,
    limit: int = 50,
    collection_handle: str | None = None,
    q: str | None = None,
    sort_by: str | None = Query(default=None, description="price-asc, price-desc, created-desc, title-asc"),
) -> Any:
    """Retrieve products with optional filtering and sorting."""
    statement = select(Product)

    if collection_handle:
        col_statement = select(Collection).where(Collection.handle == collection_handle)
        coll = session.exec(col_statement).first()
        if coll:
            statement = statement.where(Product.collection_id == coll.id)
        else:
            return ProductsPublic(data=[], count=0)

    if q:
        search_pattern = f"%{q.lower()}%"
        statement = statement.where(
            func.lower(Product.title).like(search_pattern)
            | func.lower(Product.description).like(search_pattern)
        )

    # Count total matching products
    count_statement = select(func.count()).select_from(statement.subquery())
    count = session.exec(count_statement).one()

    # Sorting
    if sort_by == "price-asc":
        statement = statement.order_by(Product.price.asc())
    elif sort_by == "price-desc":
        statement = statement.order_by(Product.price.desc())
    elif sort_by == "title-asc":
        statement = statement.order_by(Product.title.asc())
    else:
        statement = statement.order_by(Product.created_at.desc())

    statement = statement.offset(skip).limit(limit)
    products = session.exec(statement).all()

    # Build response with variants and collection title
    results = []
    for prod in products:
        item_dict = prod.model_dump()
        coll_title = prod.collection.title if prod.collection else None
        item_dict["collection_title"] = coll_title
        item_dict["variants"] = [
            ProductVariantPublic(
                id=v.id,
                product_id=v.product_id,
                title=v.title,
                sku=v.sku,
                price=v.price,
                compare_at_price=v.compare_at_price,
                available_for_sale=v.available_for_sale,
                selected_options_json=v.selected_options_json,
                image_url=v.image_url,
            )
            for v in prod.variants
        ]
        results.append(ProductPublic(**item_dict))

    return ProductsPublic(data=results, count=count)


@router.get("/{handle}", response_model=ProductPublic)
def read_product_by_handle(
    handle: str,
    session: SessionDep,
) -> Any:
    """Get single product details by handle."""
    statement = select(Product).where(Product.handle == handle)
    product = session.exec(statement).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    prod_dict = product.model_dump()
    prod_dict["collection_title"] = product.collection.title if product.collection else None
    prod_dict["variants"] = [
        ProductVariantPublic(
            id=v.id,
            product_id=v.product_id,
            title=v.title,
            sku=v.sku,
            price=v.price,
            compare_at_price=v.compare_at_price,
            available_for_sale=v.available_for_sale,
            selected_options_json=v.selected_options_json,
            image_url=v.image_url,
        )
        for v in product.variants
    ]
    return ProductPublic(**prod_dict)


@router.post("/", response_model=ProductPublic, dependencies=[Depends(get_current_active_superuser)])
def create_product(
    *,
    session: SessionDep,
    product_in: ProductCreate,
) -> Any:
    """Create a new product (Admin only)."""
    existing = session.exec(select(Product).where(Product.handle == product_in.handle)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product with this handle already exists")

    product = Product.model_validate(product_in)
    session.add(product)
    session.commit()
    session.refresh(product)

    # Create default variant
    default_variant = ProductVariant(
        product_id=product.id,
        title="Default Title",
        price=product.price,
        compare_at_price=product.compare_at_price,
        available_for_sale=product.available_for_sale,
        image_url=product.featured_image,
    )
    session.add(default_variant)
    session.commit()
    session.refresh(product)

    prod_dict = product.model_dump()
    prod_dict["collection_title"] = product.collection.title if product.collection else None
    prod_dict["variants"] = [
        ProductVariantPublic(
            id=v.id,
            product_id=v.product_id,
            title=v.title,
            sku=v.sku,
            price=v.price,
            compare_at_price=v.compare_at_price,
            available_for_sale=v.available_for_sale,
            selected_options_json=v.selected_options_json,
            image_url=v.image_url,
        )
        for v in product.variants
    ]
    return ProductPublic(**prod_dict)


@router.put("/{id}", response_model=ProductPublic, dependencies=[Depends(get_current_active_superuser)])
def update_product(
    *,
    session: SessionDep,
    id: uuid.UUID,
    product_in: ProductUpdate,
) -> Any:
    """Update product (Admin only)."""
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_dict = product_in.model_dump(exclude_unset=True)
    product.sqlmodel_update(update_dict)
    session.add(product)
    session.commit()
    session.refresh(product)

    prod_dict = product.model_dump()
    prod_dict["collection_title"] = product.collection.title if product.collection else None
    prod_dict["variants"] = [
        ProductVariantPublic(
            id=v.id,
            product_id=v.product_id,
            title=v.title,
            sku=v.sku,
            price=v.price,
            compare_at_price=v.compare_at_price,
            available_for_sale=v.available_for_sale,
            selected_options_json=v.selected_options_json,
            image_url=v.image_url,
        )
        for v in product.variants
    ]
    return ProductPublic(**prod_dict)


@router.delete("/{id}", response_model=Message, dependencies=[Depends(get_current_active_superuser)])
def delete_product(
    *,
    session: SessionDep,
    id: uuid.UUID,
) -> Any:
    """Delete a product (Admin only)."""
    product = session.get(Product, id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    session.delete(product)
    session.commit()
    return Message(message="Product deleted successfully")
