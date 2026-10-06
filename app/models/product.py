from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, String, Text, DateTime, ForeignKey, func, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    brand_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("brands.id"))
    category_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("categories.id"))
    sku: Mapped[str] = mapped_column(String(100))
    barcode: Mapped[str | None] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(500))
    slug: Mapped[str] = mapped_column(String(600))
    short_description: Mapped[str | None] = mapped_column(String(1000))
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), server_default="0")
    compare_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    stock: Mapped[int] = mapped_column(default=0)
    rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=0)
    review_count: Mapped[int] = mapped_column(default=0)
    weight: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    status: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    brand: Mapped["Brand"] = relationship(back_populates="products", lazy="joined")
    category: Mapped["Category"] = relationship(back_populates="products", lazy="joined")
    descriptions: Mapped[list["ProductDescription"]] = relationship(back_populates="product", lazy="raise", passive_deletes=True)
    images: Mapped[list["ProductImage"]] = relationship(back_populates="product", lazy="raise", passive_deletes=True)
    prices: Mapped[list["ProductPrice"]] = relationship(back_populates="product", lazy="raise", passive_deletes=True)
    reviews: Mapped[list["ProductReview"]] = relationship(back_populates="product", lazy="raise", passive_deletes=True)
    specifications: Mapped[list["ProductSpecification"]] = relationship(back_populates="product", lazy="raise", passive_deletes=True)
    variants: Mapped[list["ProductVariant"]] = relationship(back_populates="product", lazy="raise", passive_deletes=True)
    vendor_products: Mapped[list["VendorProduct"]] = relationship(back_populates="product", lazy="raise", passive_deletes=True)
