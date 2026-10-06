from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, String, DateTime, Numeric, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class VendorProduct(Base):
    __tablename__ = "vendor_products"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    vendor_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("vendors.id"))
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("products.id"))
    vendor_sku: Mapped[str | None] = mapped_column(String(100))
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), server_default="0")
    stock: Mapped[int] = mapped_column(default=0)
    status: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    vendor: Mapped["Vendor"] = relationship(back_populates="vendor_products", lazy="raise")
    product: Mapped["Product"] = relationship(back_populates="vendor_products", lazy="raise")
