from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, String, DateTime, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("products.id"))
    sku: Mapped[str] = mapped_column(String(100))
    barcode: Mapped[str | None] = mapped_column(String(50))
    variant_name: Mapped[str | None] = mapped_column(String(500))
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), server_default="0")
    compare_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    stock: Mapped[int] = mapped_column(default=0)
    weight: Mapped[Decimal | None] = mapped_column(Numeric(10, 3))
    status: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    product: Mapped["Product"] = relationship(back_populates="variants", lazy="raise")
    attributes: Mapped[list["VariantAttribute"]] = relationship(back_populates="variant", lazy="selectin", passive_deletes=True)