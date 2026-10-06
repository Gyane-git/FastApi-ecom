from datetime import datetime

from sqlalchemy import BigInteger, String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("products.id"))
    image_url: Mapped[str] = mapped_column(String(1000))
    thumbnail_url: Mapped[str | None] = mapped_column(String(1000))
    alt_text: Mapped[str | None] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(default=0)
    is_primary: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    product: Mapped["Product"] = relationship(back_populates="images", lazy="raise")
