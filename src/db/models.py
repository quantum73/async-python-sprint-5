import uuid

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(256), unique=True, nullable=False)
    password_hash = Column(String(1024), nullable=False)
    is_active = Column(Boolean, default=True)
    files = relationship("File", back_populates="user")
    created_at = Column(DateTime, index=True, server_default=func.now())


class File(Base):
    __tablename__ = "file"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(128), nullable=False)
    path = Column(String(2056), nullable=False)
    size = Column(Integer, nullable=False)
    is_downloadable = Column(Boolean, default=True)
    user_id = Column(UUID, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="files")
    created_at = Column(DateTime, index=True, server_default=func.now())
