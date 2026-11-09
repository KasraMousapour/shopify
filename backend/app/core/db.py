import json
from sqlmodel import Session, SQLModel, create_engine, select

from app import crud
from app.core.config import settings
from app.models import (
    Collection,
    Product,
    ProductVariant,
    User,
    UserCreate,
)

engine = create_engine(str(settings.DATABASE_URL), pool_pre_ping=True)


def init_db(session: Session) -> None:
    # Ensure all tables are created automatically
    SQLModel.metadata.create_all(engine)

    # 1. Seed superuser
    user = session.exec(
        select(User).where(User.email == settings.FIRST_SUPERUSER)
    ).first()
    if not user:
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            full_name="Shop Admin",
        )
        user = crud.create_user(session=session, user_create=user_in)

    # 2. Seed initial e-commerce data if empty
    existing_collection = session.exec(select(Collection)).first()
    if not existing_collection:
        # Categories / Collections
        col_apparel = Collection(
            title="Apparel",
            handle="apparel",
            description="Premium minimalist everyday clothing and streetwear.",
            image_url="https://images.unsplash.com/photo-1523381294911-8d3cead13475?w=800&auto=format&fit=crop",
        )
        col_accessories = Collection(
            title="Accessories",
            handle="accessories",
            description="Handcrafted modern accessories and lifestyle essentials.",
            image_url="https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=800&auto=format&fit=crop",
        )
        col_footwear = Collection(
            title="Footwear",
            handle="footwear",
            description="Ergonomic and iconic shoes crafted for everyday comfort.",
            image_url="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&auto=format&fit=crop",
        )
        session.add(col_apparel)
        session.add(col_accessories)
        session.add(col_footwear)
        session.commit()
        session.refresh(col_apparel)
        session.refresh(col_accessories)
        session.refresh(col_footwear)

        # Products
        products_data = [
            {
                "title": "Minimalist Heavyweight Hoodie",
                "handle": "minimalist-heavyweight-hoodie",
                "description": "Crafted from 100% organic cotton French terry, featuring drop shoulders and custom ribbing.",
                "vendor": "Acme Studios",
                "price": 95.0,
                "compare_at_price": 120.0,
                "featured_image": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800&auto=format&fit=crop",
                "collection_id": col_apparel.id,
                "options": json.dumps([{"name": "Size", "values": ["S", "M", "L", "XL"]}]),
            },
            {
                "title": "Classic Boxy Fit T-Shirt",
                "handle": "classic-boxy-fit-tshirt",
                "description": "Pre-shrunk 240 GSM combed cotton t-shirt with reinforced crew neck collar.",
                "vendor": "Acme Studios",
                "price": 45.0,
                "compare_at_price": 55.0,
                "featured_image": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800&auto=format&fit=crop",
                "collection_id": col_apparel.id,
                "options": json.dumps([{"name": "Size", "values": ["S", "M", "L"]}]),
            },
            {
                "title": "Everyday Canvas Backpack",
                "handle": "everyday-canvas-backpack",
                "description": "Water-resistant waxed cotton canvas backpack with dedicated 16-inch laptop compartment.",
                "vendor": "Acme Supply",
                "price": 110.0,
                "compare_at_price": 135.0,
                "featured_image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&auto=format&fit=crop",
                "collection_id": col_accessories.id,
                "options": json.dumps([{"name": "Color", "values": ["Olive", "Black"]}]),
            },
            {
                "title": "Ceramic Matte Travel Mug",
                "handle": "ceramic-matte-travel-mug",
                "description": "Double-walled ceramic insulated tumbler preserving beverages at optimal temperature for 12 hours.",
                "vendor": "Acme Supply",
                "price": 32.0,
                "compare_at_price": None,
                "featured_image": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=800&auto=format&fit=crop",
                "collection_id": col_accessories.id,
                "options": json.dumps([{"name": "Color", "values": ["Matte Black", "Cream"]}]),
            },
            {
                "title": "Retro Runner Sneakers",
                "handle": "retro-runner-sneakers",
                "description": "Heritage runner silhouette with premium suede overlays and high-rebound EVA midsole.",
                "vendor": "Acme Footwear",
                "price": 140.0,
                "compare_at_price": 170.0,
                "featured_image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&auto=format&fit=crop",
                "collection_id": col_footwear.id,
                "options": json.dumps([{"name": "Size", "values": ["40", "41", "42", "43", "44"]}]),
            },
            {
                "title": "Embroidered Cotton Dad Cap",
                "handle": "embroidered-cotton-dad-cap",
                "description": "Low-profile six-panel unstructured dad hat with antique brass buckle strap.",
                "vendor": "Acme Studios",
                "price": 28.0,
                "compare_at_price": 35.0,
                "featured_image": "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=800&auto=format&fit=crop",
                "collection_id": col_accessories.id,
                "options": json.dumps([{"name": "Color", "values": ["Navy", "Charcoal"]}]),
            },
        ]

        for p_data in products_data:
            options_str = p_data.pop("options")
            prod = Product(**p_data)
            session.add(prod)
            session.commit()
            session.refresh(prod)

            # Create default variant
            variant = ProductVariant(
                product_id=prod.id,
                title="Default",
                price=prod.price,
                compare_at_price=prod.compare_at_price,
                available_for_sale=True,
                selected_options_json=options_str,
                image_url=prod.featured_image,
            )
            session.add(variant)

        session.commit()
