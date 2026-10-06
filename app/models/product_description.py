from sqlalchemy import BigInteger, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ProductDescription(Base):
    __tablename__ = "product_descriptions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("products.id"))
    language_code: Mapped[str] = mapped_column(String(10))
    title: Mapped[str] = mapped_column(String(500))
    short_description: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)

    product: Mapped["Product"] = relationship(back_populates="descriptions", lazy="raise")
