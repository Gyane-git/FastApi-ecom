from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProductSpecification(Base):
    __tablename__ = "product_specifications"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("products.id"))
    specification_name: Mapped[str] = mapped_column(String(255))
    specification_value: Mapped[str] = mapped_column(String(1000))
    language_code: Mapped[str | None] = mapped_column(String(10), default="en")
    sort_order: Mapped[int] = mapped_column(default=0)

    product: Mapped["Product"] = relationship(back_populates="specifications", lazy="raise")
