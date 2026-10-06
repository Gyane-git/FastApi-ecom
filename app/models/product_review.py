from datetime import datetime

from sqlalchemy import BigInteger, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProductReview(Base):
    __tablename__ = "product_reviews"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("products.id"))
    user_id: Mapped[int | None] = mapped_column(BigInteger)
    rating: Mapped[int] = mapped_column()
    title: Mapped[str | None] = mapped_column(String(255))
    review: Mapped[str | None] = mapped_column(Text)
    is_verified_purchase: Mapped[int] = mapped_column(default=0)
    status: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    product: Mapped["Product"] = relationship(back_populates="reviews", lazy="raise")
