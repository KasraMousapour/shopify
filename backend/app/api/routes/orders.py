import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.models import (
    Cart,
    Message,
    Order,
    OrderCreate,
    OrderItem,
    OrderItemPublic,
    OrderPublic,
    OrdersPublic,
)

router = APIRouter(prefix="/orders", tags=["orders"])


def build_order_public(order: Order) -> OrderPublic:
    items = [
        OrderItemPublic(
            id=item.id,
            product_id=item.product_id,
            product_title=item.product_title,
            variant_title=item.variant_title,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=round(item.quantity * item.unit_price, 2),
        )
        for item in order.items
    ]
    return OrderPublic(
        id=order.id,
        order_number=order.order_number,
        customer_email=order.customer_email,
        customer_name=order.customer_name,
        total_amount=order.total_amount,
        currency=order.currency,
        status=order.status,
        shipping_address=order.shipping_address,
        created_at=order.created_at,
        items=items,
    )


@router.post("/checkout", response_model=OrderPublic)
def checkout_cart(
    order_in: OrderCreate,
    session: SessionDep,
) -> Any:
    """Create an order from an active shopping cart."""
    cart = session.get(Cart, order_in.cart_id)
    if not cart or not cart.lines:
        raise HTTPException(status_code=400, detail="Cart is empty or not found")

    subtotal = sum(line.quantity * line.unit_price for line in cart.lines)
    order_num = f"ORD-{uuid.uuid4().hex[:8].upper()}"

    order = Order(
        order_number=order_num,
        user_id=cart.user_id,
        customer_email=order_in.customer_email,
        customer_name=order_in.customer_name,
        total_amount=round(subtotal, 2),
        currency=cart.currency,
        status="paid",
        shipping_address=order_in.shipping_address,
    )
    session.add(order)
    session.commit()
    session.refresh(order)

    # Transfer lines to order items
    for line in cart.lines:
        prod_title = line.product.title if line.product else "Product"
        var_title = line.variant.title if line.variant else None
        order_item = OrderItem(
            order_id=order.id,
            product_id=line.product_id,
            variant_id=line.variant_id,
            product_title=prod_title,
            variant_title=var_title,
            quantity=line.quantity,
            unit_price=line.unit_price,
        )
        session.add(order_item)
        session.delete(line)

    session.commit()
    session.refresh(order)
    return build_order_public(order)


@router.get("/", response_model=OrdersPublic, dependencies=[Depends(get_current_active_superuser)])
def read_orders(
    session: SessionDep,
    skip: int = 0,
    limit: int = 50,
) -> Any:
    """Retrieve all orders (Admin only)."""
    count_statement = select(func.count()).select_from(Order)
    count = session.exec(count_statement).one()

    statement = select(Order).order_by(Order.created_at.desc()).offset(skip).limit(limit)
    orders = session.exec(statement).all()

    return OrdersPublic(data=[build_order_public(o) for o in orders], count=count)


@router.get("/{order_id}", response_model=OrderPublic)
def get_order(order_id: uuid.UUID, session: SessionDep) -> Any:
    """Get order details by id."""
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return build_order_public(order)
