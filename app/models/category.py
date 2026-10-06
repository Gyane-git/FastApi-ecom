from datetime import datetime

from sqlalchemy import BigInteger, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    parent_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("categories.id"))
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(1000))
    level: Mapped[int] = mapped_column(default=0)
    status: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    parent: Mapped["Category | None"] = relationship(remote_side=[id], back_populates="children", lazy="raise")
    children: Mapped[list["Category"]] = relationship(back_populates="parent", lazy="raise")
    products: Mapped[list["Product"]] = relationship(back_populates="category", lazy="raise")
