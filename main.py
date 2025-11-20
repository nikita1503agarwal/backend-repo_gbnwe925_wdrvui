import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson.objectid import ObjectId

from database import db, create_document, get_documents
from schemas import Figurine, Order

app = FastAPI(title="MJ Figurines API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "MJ Figurines API running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = getattr(db, 'name', '✅ Connected')
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# Initialize the single figurine product if not present
@app.on_event("startup")
async def seed_figurine_product():
    if db is None:
        return
    # Check if a figurine exists
    existing = db["figurine"].find_one({"name": "Michael Jackson Collectible Figurine"})
    if not existing:
        product = Figurine(
            name="Michael Jackson Collectible Figurine",
            width_cm=10.0,
            height_cm=30.0,
            material="Plastic",
            price_usd=49.99,
            images=[
                "https://images.unsplash.com/photo-1520974697809-9343d26503bc?q=80&w=1200&auto=format&fit=crop",
            ],
            description=(
                "Premium detailed figurine inspired by the King of Pop. 10 cm wide, 30 cm tall, "
                "molded in durable plastic with a customizable nameplate on the base."
            ),
            customizable_base=True,
        )
        create_document("figurine", product)

@app.get("/api/product", response_model=Figurine)
def get_product():
    doc = db["figurine"].find_one({}, sort=[("_id", 1)]) if db is not None else None
    if not doc:
        # Fallback if DB not available: return static product (non-persistent)
        return Figurine(
            name="Michael Jackson Collectible Figurine",
            width_cm=10.0,
            height_cm=30.0,
            material="Plastic",
            price_usd=49.99,
            images=[
                "https://images.unsplash.com/photo-1520974697809-9343d26503bc?q=80&w=1200&auto=format&fit=crop",
            ],
            description=(
                "Premium detailed figurine inspired by the King of Pop. 10 cm wide, 30 cm tall, "
                "molded in durable plastic with a customizable nameplate on the base."
            ),
            customizable_base=True,
        )
    # Map db doc to Figurine
    return Figurine(
        name=doc.get("name"),
        width_cm=float(doc.get("width_cm", 10.0)),
        height_cm=float(doc.get("height_cm", 30.0)),
        material=doc.get("material", "Plastic"),
        price_usd=float(doc.get("price_usd", 49.99)),
        images=doc.get("images"),
        description=doc.get("description"),
        customizable_base=bool(doc.get("customizable_base", True)),
    )

class OrderIn(BaseModel):
    custom_name: str
    quantity: int
    customer_name: str
    customer_email: str
    shipping_address: str
    notes: Optional[str] = None

class OrderOut(BaseModel):
    order_id: str
    total_usd: float

@app.post("/api/order", response_model=OrderOut)
def create_order(payload: OrderIn):
    # Basic constraints
    if len(payload.custom_name.strip()) == 0 or len(payload.custom_name.strip()) > 24:
        raise HTTPException(status_code=400, detail="Custom name must be 1-24 characters.")
    if payload.quantity < 1 or payload.quantity > 10:
        raise HTTPException(status_code=400, detail="Quantity must be between 1 and 10.")

    # Get product price
    product_doc = db["figurine"].find_one({}, sort=[("_id", 1)]) if db is not None else None
    unit_price = float(product_doc.get("price_usd", 49.99)) if product_doc else 49.99

    subtotal = unit_price * payload.quantity
    engraving_fee = 4.0 if payload.custom_name.strip() else 0.0
    shipping = 6.99
    total = round(subtotal + engraving_fee + shipping, 2)

    order = Order(
        product_id=str(product_doc.get("_id")) if product_doc else None,
        custom_name=payload.custom_name.strip(),
        quantity=payload.quantity,
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        shipping_address=payload.shipping_address,
        unit_price_usd=unit_price,
        total_usd=total,
        notes=payload.notes,
    )

    if db is not None:
        oid = create_document("order", order)
        return OrderOut(order_id=oid, total_usd=total)
    else:
        # Fallback non-persistent
        return OrderOut(order_id="demo-order", total_usd=total)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
