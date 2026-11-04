from sqlmodel import Field, SQLModel


class Category(SQLModel, table=True):
    __tablename__ = "Categories"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)


class Product(SQLModel, table=True):
    __tablename__ = "Products"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    sku: str = Field(max_length=50)  # Артикул для валідації через regex
    price: float
    stock_quantity: int
    category_id: int | None = Field(default=None, foreign_key="Categories.id")
