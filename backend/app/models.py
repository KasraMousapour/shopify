import uuid
from datetime import UTC, datetime

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(UTC)


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    is_superuser: bool | None = None
    full_name: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(default_factory=get_datetime_utc)
    items: list[Item] = Relationship(back_populates="owner", cascade_delete=True)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(default_factory=get_datetime_utc)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
# ==========================================
# E-Commerce Models
# ==========================================

# --- Collections (Categories) ---
class CollectionBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    handle: str = Field(unique=True, index=True, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    image_url: str | None = Field(default=None, max_length=1000)


class CollectionCreate(CollectionBase):
    pass


class CollectionUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    handle: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    image_url: str | None = Field(default=None, max_length=1000)


class Collection(CollectionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(default_factory=get_datetime_utc)
    products: list['Product'] = Relationship(back_populates='collection')


class CollectionPublic(CollectionBase):
    id: uuid.UUID
    created_at: datetime | None = None


class CollectionsPublic(SQLModel):
    data: list[CollectionPublic]
    count: int


# --- Products & Variants ---
class ProductBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    handle: str = Field(unique=True, index=True, max_length=255)
    description: str | None = Field(default=None)
    vendor: str | None = Field(default='Shopify Store', max_length=255)
    price: float = Field(ge=0)
    compare_at_price: float | None = Field(default=None, ge=0)
    currency: str = Field(default='USD', max_length=10)
    featured_image: str | None = Field(default=None, max_length=1000)
    images_json: str | None = Field(default=None)  # JSON array of URLs
    available_for_sale: bool = Field(default=True)
    is_gift_card: bool = Field(default=False)
    collection_id: uuid.UUID | None = Field(default=None, foreign_key='collection.id')


class ProductCreate(ProductBase):
    pass


class ProductUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    handle: str | None = Field(default=None, max_length=255)
    description: str | None = None
    vendor: str | None = None
    price: float | None = Field(default=None, ge=0)
    compare_at_price: float | None = None
    currency: str | None = None
    featured_image: str | None = None
    images_json: str | None = None
    available_for_sale: bool | None = None
    is_gift_card: bool | None = None
    collection_id: uuid.UUID | None = None


class Product(ProductBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(default_factory=get_datetime_utc)
    collection: Collection | None = Relationship(back_populates='products')
    variants: list['ProductVariant'] = Relationship(back_populates='product', cascade_delete=True)


class ProductVariantBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    sku: str | None = Field(default=None, max_length=100)
    price: float = Field(ge=0)
    compare_at_price: float | None = Field(default=None, ge=0)
    available_for_sale: bool = Field(default=True)
    selected_options_json: str | None = Field(default=None)  # JSON e.g. {'Size': 'M', 'Color': 'Black'}
    image_url: str | None = Field(default=None, max_length=1000)


class ProductVariantCreate(ProductVariantBase):
    product_id: uuid.UUID


class ProductVariant(ProductVariantBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    product_id: uuid.UUID = Field(foreign_key='product.id', nullable=False, ondelete='CASCADE')
    product: Product | None = Relationship(back_populates='variants')


class ProductVariantPublic(ProductVariantBase):
    id: uuid.UUID
    product_id: uuid.UUID


class ProductPublic(ProductBase):
    id: uuid.UUID
    created_at: datetime | None = None
    collection_title: str | None = None
    variants: list[ProductVariantPublic] = []


class ProductsPublic(SQLModel):
    data: list[ProductPublic]
    count: int


# --- Cart & Cart Items ---
class CartItem(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    cart_id: uuid.UUID = Field(foreign_key='cart.id', nullable=False, ondelete='CASCADE')
    product_id: uuid.UUID = Field(foreign_key='product.id', nullable=False)
    variant_id: uuid.UUID | None = Field(default=None, foreign_key='productvariant.id')
    quantity: int = Field(default=1, ge=1)
    unit_price: float = Field(ge=0)
    cart: 'Cart' = Relationship(back_populates='lines')
    product: Product = Relationship()
    variant: ProductVariant | None = Relationship()


class Cart(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    session_id: str | None = Field(default=None, index=True, max_length=255)
    user_id: uuid.UUID | None = Field(default=None, foreign_key='user.id')
    currency: str = Field(default='USD', max_length=10)
    created_at: datetime | None = Field(default_factory=get_datetime_utc)
    updated_at: datetime | None = Field(default_factory=get_datetime_utc)
    lines: list[CartItem] = Relationship(back_populates='cart', cascade_delete=True)


class CartItemAdd(SQLModel):
    product_id: uuid.UUID
    variant_id: uuid.UUID | None = None
    quantity: int = Field(default=1, ge=1)


class CartItemUpdate(SQLModel):
    quantity: int = Field(ge=0)


class CartItemPublic(SQLModel):
    id: uuid.UUID
    product_id: uuid.UUID
    product_title: str
    product_handle: str
    product_image: str | None = None
    variant_id: uuid.UUID | None = None
    variant_title: str | None = None
    quantity: int
    unit_price: float
    total_price: float


class CartPublic(SQLModel):
    id: uuid.UUID
    currency: str
    total_quantity: int
    subtotal_amount: float
    lines: list[CartItemPublic]


# --- Orders ---
class OrderItem(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    order_id: uuid.UUID = Field(foreign_key='order.id', nullable=False, ondelete='CASCADE')
    product_id: uuid.UUID = Field(foreign_key='product.id')
    variant_id: uuid.UUID | None = None
    product_title: str = Field(max_length=255)
    variant_title: str | None = Field(default=None, max_length=255)
    quantity: int = Field(ge=1)
    unit_price: float = Field(ge=0)
    order: 'Order' = Relationship(back_populates='items')


class Order(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    order_number: str = Field(unique=True, index=True, max_length=50)
    user_id: uuid.UUID | None = Field(default=None, foreign_key='user.id')
    customer_email: EmailStr = Field(max_length=255)
    customer_name: str = Field(max_length=255)
    total_amount: float = Field(ge=0)
    currency: str = Field(default='USD', max_length=10)
    status: str = Field(default='pending', max_length=50)
    shipping_address: str | None = Field(default=None)
    created_at: datetime | None = Field(default_factory=get_datetime_utc)
    items: list[OrderItem] = Relationship(back_populates='order', cascade_delete=True)


class OrderCreate(SQLModel):
    cart_id: uuid.UUID
    customer_email: EmailStr
    customer_name: str
    shipping_address: str


class OrderItemPublic(SQLModel):
    id: uuid.UUID
    product_id: uuid.UUID
    product_title: str
    variant_title: str | None = None
    quantity: int
    unit_price: float
    total_price: float


class OrderPublic(SQLModel):
    id: uuid.UUID
    order_number: str
    customer_email: EmailStr
    customer_name: str
    total_amount: float
    currency: str
    status: str
    shipping_address: str | None = None
    created_at: datetime | None = None
    items: list[OrderItemPublic]


class OrdersPublic(SQLModel):
    data: list[OrderPublic]
    count: int
