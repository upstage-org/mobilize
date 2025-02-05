from datetime import datetime
from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
)
from sqlalchemy.orm import relationship
from global_config import BaseModel


class AssetModel(BaseModel):
    __tablename__ = "asset"
    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    asset_type_id = Column(
        Integer, ForeignKey("asset_type.id"), nullable=False, default=0
    )
    owner_id = Column(Integer, ForeignKey("upstage_user.id"), nullable=False, default=0)
    description = Column(Text, nullable=True)
    file_location = Column(Text, nullable=False)
    created_on = Column(TIMESTAMP(timezone=True), default=datetime.now)
    updated_on = Column(TIMESTAMP(timezone=True), default=datetime.now)
    size = Column(BigInteger, nullable=False, default=0)
    copyright_level = Column(Integer, nullable=False, default=0)
    dormant = Column(Boolean, nullable=False, default=False)
    asset_type = relationship("AssetTypeModel", foreign_keys=[asset_type_id])
    owner = relationship("UserModel", foreign_keys=[owner_id])
    asset_license = relationship("AssetLicenseModel", uselist=False, backref="asset")
    stages = relationship(
        "ParentStageModel", lazy="dynamic", back_populates="child_asset"
    )
    tags = relationship("MediaTagModel", lazy="dynamic", back_populates="asset")
    permissions = relationship(
        "AssetUsageModel", lazy="dynamic", back_populates="asset"
    )


class AvatarVoice:
    voice: String
    variant: String
    pitch: Integer
    speed: Integer
    amplitude: Integer


class Voice:
    voice: AvatarVoice
    avatar: AssetModel
