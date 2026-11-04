import re
from typing import List
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select, SQLModel

from database import engine, get_session
from models import Product

app = FastAPI(title="Ceramics Production API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    SQLModel.metadata.create_all(engine)

@app.get("/products/", response_model=List[Product])
def get_products(session: Session = Depends(get_session)):
    return session.exec(select(Product)).all()


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Виріб не знайдено")
    return product


@app.post("/products/", response_model=Product)
def create_product(product: Product, session: Session = Depends(get_session)):
    if product.sku and not re.match(r"^SKU-\d{4}$", product.sku):
        raise HTTPException(status_code=400, detail="Невірний формат SKU. Повинно бути у форматі SKU-XXXX.")

    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@app.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, updated_product: Product, session: Session = Depends(get_session)):
    if updated_product.sku and not re.match(r"^SKU-\d{4}$", updated_product.sku):
        raise HTTPException(status_code=400, detail="Невірний формат SKU. Повинно бути у форматі SKU-XXXX.")

    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Виріб не знайдено")

    db_product.name = updated_product.name
    db_product.sku = updated_product.sku
    db_product.price = updated_product.price
    db_product.stock_quantity = updated_product.stock_quantity
    db_product.category_id = updated_product.category_id

    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


@app.delete("/products/{product_id}")
def delete_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Виріб не знайдено")

    session.delete(product)
    session.commit()
    return {"message": f"Виріб з ID {product_id} успішно видалено"}


#http://127.0.0.1:8000/docs