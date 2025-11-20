"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# Example schemas (kept for reference/use by DB viewer)
class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Application-specific schemas
class Figurine(BaseModel):
    """
    Figurine product schema (single product for this shop)
    Collection name: "figurine"
    """
    name: str = Field(..., description="Display name of the figurine")
    width_cm: float = Field(..., ge=0, description="Width in centimeters")
    height_cm: float = Field(..., ge=0, description="Height in centimeters")
    material: str = Field(..., description="Primary material")
    price_usd: float = Field(..., ge=0, description="Base price in USD")
    images: Optional[List[str]] = Field(default=None, description="Image URLs")
    description: Optional[str] = None
    customizable_base: bool = Field(True, description="Whether the base name is customizable")

class Order(BaseModel):
    """
    Orders collection schema
    Collection name: "order"
    """
    product_id: Optional[str] = Field(None, description="Associated product identifier")
    custom_name: str = Field(..., min_length=1, max_length=24, description="Name to engrave on the base")
    quantity: int = Field(1, ge=1, le=10, description="Quantity ordered")

    customer_name: str = Field(..., description="Customer full name")
    customer_email: EmailStr = Field(..., description="Customer email")
    shipping_address: str = Field(..., min_length=8, description="Full shipping address")

    unit_price_usd: float = Field(..., ge=0, description="Unit price at time of order")
    total_usd: float = Field(..., ge=0, description="Computed total price")
    notes: Optional[str] = Field(None, description="Optional order notes")

# Note: The Flames database viewer can use these schemas for validation.
