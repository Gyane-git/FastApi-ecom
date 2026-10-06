from decimal import Decimal

from sqlalchemy import BigInteger, String, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProductPrice(Base):
    __tablename__ = "product_prices"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("products.id"))
    country_code: Mapped[str] = mapped_column(String(10))
    currency_code: Mapped[str] = mapped_column(String(10))
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    compare_price: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    is_active: Mapped[int] = mapped_column(default=1)

    product: Mapped["Product"] = relationship(back_populates="prices", lazy="raise")
