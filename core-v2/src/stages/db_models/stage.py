from datetime import datetime
from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from global_config import BaseModel
from stages.db_models.stage_attribute import StageAttributeModel


class StageModel(BaseModel):
    """
    Stage is yet another asset type, with its own attributes,
    but is broken out for convenience of group licensing/permissions.
    """

    __tablename__ = "stage"
    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("upstage_user.id"), nullable=False, default=0)
    file_location = Column(Text, nullable=False)
    created_on = Column(DateTime, nullable=False, default=datetime.now)
    last_access = Column(DateTime, nullable=True)
    owner = relationship("UserModel", foreign_keys=[owner_id])
    attributes = relationship(
        lambda: StageAttributeModel, lazy="dynamic", back_populates="stage"
    )
    assets = relationship("ParentStageModel", lazy="dynamic", back_populates="stage")

    @hybrid_property
    def cover(self):
        return (
            self.attributes.filter(StageAttributeModel.name == "cover")
            .first()
            .description
        )

    @hybrid_property
    def visibility(self):
        return (
            self.attributes.filter(StageAttributeModel.name == "visibility")
            .first()
            .description
            == "true"
        )

    @hybrid_property
    def status(self):
        return (
            self.attributes.filter(StageAttributeModel.name == "status")
            .first()
            .description
        )
