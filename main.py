import re

from fastapi import Body, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, SQLModel, select

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


# БАЗА


@app.get("/products/", response_model=list[Product])
def get_products(session: Session = Depends(get_session)):  # noqa: B008
    return session.exec(select(Product)).all()


@app.get("/products/{product_id}", response_model=Product)
def get_product(product_id: int, session: Session = Depends(get_session)):  # noqa: B008
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Виріб не знайдено")
    return product


@app.post("/products/", response_model=Product)
def create_product(product: Product, session: Session = Depends(get_session)):  # noqa: B008
    if product.sku and not re.match(r"^SKU-\d{4}$", product.sku):
        raise HTTPException(
            status_code=400,
            detail="Невірний формат SKU. Повинно бути у форматі SKU-XXXX.",
        )

    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@app.put("/products/{product_id}", response_model=Product)
def update_product(
    product_id: int, updated_product: Product, session: Session = Depends(get_session)
):  # noqa: B008
    if updated_product.sku and not re.match(r"^SKU-\d{4}$", updated_product.sku):
        raise HTTPException(
            status_code=400,
            detail="Невірний формат SKU. Повинно бути у форматі SKU-XXXX.",
        )

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
def delete_product(product_id: int, session: Session = Depends(get_session)):  # noqa: B008
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Виріб не знайдено")

    session.delete(product)
    session.commit()
    return {"message": f"Виріб з ID {product_id} успішно видалено"}


# СТОРІНКА

items: list[dict] = [
    {
        "id": 1,
        "title": "Глечик",
        "type": "Майоліка",
        "year": 2024,
        "price": 450,
        "purpose": "побутове",
        "isTypical": True,
    },
    {
        "id": 2,
        "title": "Ваза",
        "type": "Теракота",
        "year": 2025,
        "price": 1200,
        "purpose": "декоративне",
        "isTypical": False,
    },
    {
        "id": 3,
        "title": "Високовольтний ізолятор",
        "type": "Технічна кераміка",
        "year": 2026,
        "price": 850,
        "purpose": "технічне",
        "isTypical": True,
    },
]
next_id = 1


def validate_item(data: dict) -> str | None:
    title, type_ = data.get("title"), data.get("type")
    year, price = data.get("year"), data.get("price")
    purpose, is_typical = data.get("purpose"), data.get("isTypical")

    if not isinstance(title, str) or not title.strip():
        return "Вкажіть назву виробу"
    if not isinstance(type_, str) or not type_.strip():
        return "Вкажіть тип кераміки"
    if isinstance(year, bool) or not isinstance(year, int):
        return "Рік має бути цілим числом"
    if not 1900 <= year <= 2026:
        return "Некоректний рік"
    if isinstance(price, bool) or not isinstance(price, (int, float)):
        return "Ціна має бути числом"
    if price <= 0:
        return "Ціна має бути більшою за 0"
    if not isinstance(purpose, str) or not purpose.strip():
        return "Вкажіть призначення"
    if not isinstance(is_typical, bool):
        return "Некоректне значення isTypical"
    return None


@app.get("/api/items", tags=["Сторінка"])
def list_items():
    return items


@app.post("/api/items", status_code=201, tags=["Сторінка"])
def add_item(payload: dict = Body(...)):  # noqa: B008
    global next_id
    error = validate_item(payload)
    if error:
        raise HTTPException(status_code=400, detail=error)

    item = {
        "id": next_id,
        "title": payload["title"].strip(),
        "type": payload["type"].strip(),
        "year": payload["year"],
        "price": payload["price"],
        "purpose": payload["purpose"],
        "isTypical": payload["isTypical"],
    }
    next_id += 1
    items.append(item)
    return item


@app.delete("/api/items/{item_id}", tags=["Сторінка"])
def remove_item(item_id: int):
    for index, item in enumerate(items):
        if item["id"] == item_id:
            return items.pop(index)
    raise HTTPException(status_code=404, detail="Запис не знайдено")

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


# http://127.0.0.1:8000/docs

# {
#   "id": 1,
#   "name": "Керамічна чашка ручної роботи",
#   "sku": "SKU-1001",
#   "price": 350.0,
#   "stock_quantity": 15,
#   "category_id": 1
# }

# {
#   "title": "Тестова чашка",
#   "type": "Майоліка",
#   "year": 2025,
#   "price": 300,
#   "purpose": "побутове",
#   "isTypical": true
# }