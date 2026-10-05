from sqlalchemy import Boolean, String, true
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin


class Language(Base, TimestampMixin):
    """A language offered by the platform (ISO 639-1 code as natural key)."""

    __tablename__ = "languages"

    code: Mapped[str] = mapped_column(String(8), primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    native_name: Mapped[str] = mapped_column(String(64), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true(), nullable=False)
