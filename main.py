import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from database import create_document
from schemas import Reservation

app = FastAPI(title="Hamacas Suazo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hamacas Suazo Backend Running"}

# Public products definition (static). Images will be served by frontend public assets
class Product(BaseModel):
    id: str
    name_es: str
    name_en: str
    description_es: str
    description_en: str
    base_price: float
    colors: List[str]
    images: dict  # {color: path}


def build_products() -> List[Product]:
    # Color palette names used across site
    color_map = ["tabaco", "marfil", "negro", "blanco"]
    base = "/products"
    return [
        Product(
            id="matrimonial",
            name_es="Matrimonial",
            name_en="Matrimonial",
            description_es="Amplia, elegante y perfecta para compartir.",
            description_en="Spacious, elegant and perfect for two.",
            base_price=220.0,
            colors=color_map,
            images={c: f"{base}/matrimonial/{c}.jpg" for c in color_map},
        ),
        Product(
            id="unipersonal",
            name_es="Unipersonal",
            name_en="Single",
            description_es="Clásica y cómoda para relajarse.",
            description_en="Classic and comfortable for daily rest.",
            base_price=140.0,
            colors=color_map,
            images={c: f"{base}/unipersonal/{c}.jpg" for c in color_map},
        ),
        Product(
            id="familiar",
            name_es="Familiar",
            name_en="Family",
            description_es="Resistente y amplia para toda la familia.",
            description_en="Durable and roomy for the whole family.",
            base_price=280.0,
            colors=color_map,
            images={c: f"{base}/familiar/{c}.jpg" for c in color_map},
        ),
        Product(
            id="hamacasilla",
            name_es="Hamacasilla",
            name_en="Hammock Chair",
            description_es="Silla colgante artesanal para espacios íntimos.",
            description_en="Artisanal hanging chair for cozy corners.",
            base_price=160.0,
            colors=color_map,
            images={c: f"{base}/hamacasilla/{c}.jpg" for c in color_map},
        ),
        Product(
            id="chino",
            name_es="Chino",
            name_en="Chino",
            description_es="Trenzado fino con estética minimalista.",
            description_en="Fine weave with minimal aesthetic.",
            base_price=180.0,
            colors=color_map,
            images={c: f"{base}/chino/{c}.jpg" for c in color_map},
        ),
        Product(
            id="montanera",
            name_es="Montañera",
            name_en="Montañera",
            description_es="Inspirada en la tradición, ideal para exteriores.",
            description_en="Tradition-inspired, perfect for outdoors.",
            base_price=200.0,
            colors=color_map,
            images={c: f"{base}/montanera/{c}.jpg" for c in color_map},
        ),
        Product(
            id="ninos",
            name_es="Niños",
            name_en="Kids",
            description_es="Segura y divertida para los más pequeños.",
            description_en="Safe and fun for the little ones.",
            base_price=110.0,
            colors=color_map,
            images={c: f"{base}/ninos/{c}.jpg" for c in color_map},
        ),
    ]


@app.get("/api/products", response_model=List[Product])
def list_products():
    return build_products()


class ReservationIn(BaseModel):
    name: str
    color: str
    hammock_type: str
    phone: str
    message: Optional[str] = None


@app.post("/api/reservations")
def create_reservation(payload: ReservationIn):
    # Basic validation for known product and color
    products = {p.id: p for p in build_products()}
    if payload.hammock_type not in products:
        raise HTTPException(status_code=400, detail="Invalid hammock type")
    if payload.color not in products[payload.hammock_type].colors:
        raise HTTPException(status_code=400, detail="Invalid color for selected product")

    # Persist to DB
    data = Reservation(
        name=payload.name,
        color=payload.color,
        hammock_type=payload.hammock_type,
        phone=payload.phone,
        message=payload.message,
    )
    try:
        reservation_id = create_document("reservation", data)
    except Exception as e:
        # If DB unavailable, still acknowledge but signal degraded mode
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {"status": "ok", "reservation_id": reservation_id}


@app.get("/test")
def test_database():
    """Simple health check"""
    from database import db
    return {
        "backend": "running",
        "db_connected": bool(db is not None),
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
