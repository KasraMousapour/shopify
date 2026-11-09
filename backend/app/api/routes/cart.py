import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import SessionDep
from app.models import (
    Cart,
    CartItem,
    CartItemAdd,
    CartItemPublic,
    CartItemUpdate,
    CartPublic,
    Product,
    ProductVariant,
)

router = APIRouter(prefix="/cart", tags=["cart"])


def build_cart_public(cart: Cart) -> CartPublic:
    lines: list[CartItemPublic] = []
    total_qty = 0
    subtotal = 0.0

    for item in cart.lines:
        line_total = item.quantity * item.unit_price
        total_qty += item.quantity
        subtotal += line_total

        prod_title = item.product.title if item.product else "Unknown Product"
        prod_handle = item.product.handle if item.product else ""
        prod_image = item.product.featured_image if item.product else None
        variant_title = item.variant.title if item.variant else None

        lines.append(
            CartItemPublic(
                id=item.id,
                product_id=item.product_id,
                product_title=prod_title,
                product_handle=prod_handle,
                product_image=prod_image,
                variant_id=item.variant_id,
                variant_title=variant_title,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=line_total,
            )
        )

    return CartPublic(
        id=cart.id,
        currency=cart.currency,
        total_quantity=total_qty,
        subtotal_amount=round(subtotal, 2),
        lines=lines,
    )


@router.post("/", response_model=CartPublic)
def create_cart(session: SessionDep) -> Any:
    """Create a new shopping cart."""
    cart = Cart()
    session.add(cart)
    session.commit()
    session.refresh(cart)
    return build_cart_public(cart)


@router.get("/{cart_id}", response_model=CartPublic)
def get_cart(cart_id: uuid.UUID, session: SessionDep) -> Any:
    """Get cart by id with all active lines."""
    cart = session.get(Cart, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return build_cart_public(cart)


@router.post("/{cart_id}/lines", response_model=CartPublic)
def add_cart_line(
    cart_id: uuid.UUID,
    item_in: CartItemAdd,
    session: SessionDep,
) -> Any:
    """Add a product or variant line to cart."""
    cart = session.get(Cart, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    product = session.get(Product, item_in.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    unit_price = product.price
    if item_in.variant_id:
        variant = session.get(ProductVariant, item_in.variant_id)
        if variant:
            unit_price = variant.price

    # Check if item already exists in cart
    existing_item = next(
        (
            item
            for item in cart.lines
            if item.product_id == item_in.product_id
            and item.variant_id == item_in.variant_id
        ),
        None,
    )

    if existing_item:
        existing_item.quantity += item_in.quantity
        session.add(existing_item)
    else:
        new_item = CartItem(
            cart_id=cart.id,
            product_id=item_in.product_id,
            variant_id=item_in.variant_id,
            quantity=item_in.quantity,
            unit_price=unit_price,
        )
        session.add(new_item)

    cart.updated_at = datetime.now(timezone.utc)
    session.add(cart)
    session.commit()
    session.refresh(cart)
    return build_cart_public(cart)


@router.put("/{cart_id}/lines/{line_id}", response_model=CartPublic)
def update_cart_line(
    cart_id: uuid.UUID,
    line_id: uuid.UUID,
    item_in: CartItemUpdate,
    session: SessionDep,
) -> Any:
    """Update quantity for a cart line."""
    cart = session.get(Cart, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    line = session.get(CartItem, line_id)
    if not line or line.cart_id != cart_id:
        raise HTTPException(status_code=404, detail="Cart item not found")

    if item_in.quantity <= 0:
        session.delete(line)
    else:
        line.quantity = item_in.quantity
        session.add(line)

    cart.updated_at = datetime.now(timezone.utc)
    session.add(cart)
    session.commit()
    session.refresh(cart)
    return build_cart_public(cart)


@router.delete("/{cart_id}/lines/{line_id}", response_model=CartPublic)
def remove_cart_line(
    cart_id: uuid.UUID,
    line_id: uuid.UUID,
    session: SessionDep,
) -> Any:
    """Remove line from cart."""
    cart = session.get(Cart, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    line = session.get(CartItem, line_id)
    if not line or line.cart_id != cart_id:
        raise HTTPException(status_code=404, detail="Cart item not found")

    session.delete(line)
    cart.updated_at = datetime.now(timezone.utc)
    session.add(cart)
    session.commit()
    session.refresh(cart)
    return build_cart_public(cart)
