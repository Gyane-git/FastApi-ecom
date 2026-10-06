from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class VariantAttribute(Base):
    __tablename__ = "variant_attributes"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    variant_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("product_variants.id"))
    attribute_name: Mapped[str] = mapped_column(String(100))
    attribute_value: Mapped[str] = mapped_column(String(255))

    variant: Mapped["ProductVariant"] = relationship(back_populates="attributes", lazy="raise")
