from datetime import datetime
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from core.entities.base import BaseEntity


class AssetUsageEntity(BaseEntity):
    __tablename__ = "asset_usage"
    id = Column(BigInteger, primary_key=True)
    asset_id = Column(Integer, ForeignKey("asset.id"), nullable=False, default=0)
    user_id = Column(Integer, ForeignKey("upstage_user.id"), nullable=False, default=0)
    approved = Column(Boolean, nullable=False, default=False)
    seen = Column(Boolean, nullable=False, default=False)
    note = Column(String, nullable=True)
    created_on = Column(DateTime, nullable=False, default=datetime.utcnow)
    user = relationship("UserEntity", foreign_keys=[user_id])
    asset = relationship("AssetEntity", foreign_keys=[asset_id])
