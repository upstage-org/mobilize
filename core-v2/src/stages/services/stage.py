import re
from datetime import datetime
from graphql import GraphQLError
from sqlalchemy import and_
from global_config import DBSession, ScopedSession, convert_keys_to_camel_case

from users.db_models.user import ADMIN, SUPER_ADMIN
from stages.http.validation import DuplicateStageInput, StageInput

from event_archive.db_models.event import EventModel
from performance_config.db_models.performance import PerformanceModel
from performance_config.db_models.scene import SceneModel
from stages.db_models.parent_stage import ParentStageModel
from stages.db_models.stage import StageModel
from stages.db_models.stage_attribute import StageAttributeModel
from users.db_models.user import UserModel


class StageService:
    def __init__(self):
        pass

    def create_stage(self, user: UserModel, input: StageInput):
        with ScopedSession() as local_db_session:
            stage = StageModel(
                name=input.name,
                description=input.description,
                owner_id=user.id,
                file_location=input.fileLocation,
            )

            local_db_session.add(stage)
            local_db_session.commit()

            local_db_session.refresh(stage)
            self.update_stage_attribute(
                stage.id, "cover", input.cover, local_db_session
            )
            self.update_stage_attribute(
                stage.id, "visibility", str(input.visibility), local_db_session
            )
            self.update_stage_attribute(
                stage.id, "description", input.description, local_db_session
            )
            self.update_stage_attribute(
                stage.id, "status", input.status, local_db_session
            )
            self.update_stage_attribute(
                stage.id, "playerAccess", input.playerAccess, local_db_session
            )
            local_db_session.commit()
            local_db_session.flush()
            return convert_keys_to_camel_case(stage.to_dict())

    def update_stage(self, user: UserModel, input: StageInput):
        with ScopedSession() as local_db_session:
            stage = local_db_session.query(StageModel).filter_by(id=input.id).first()
            if not stage or not input.id:
                raise GraphQLError("Stage not found")

            stage.name = input.name
            stage.description = input.description
            stage.file_location = input.fileLocation
            self.update_stage_attribute(
                stage.id, "cover", input.cover, local_db_session
            )
            self.update_stage_attribute(
                stage.id, "visibility", str(input.visibility), local_db_session
            )
            self.update_stage_attribute(
                stage.id, "description", input.description, local_db_session
            )
            self.update_stage_attribute(
                stage.id, "status", input.status, local_db_session
            )
            self.update_stage_attribute(
                stage.id, "playerAccess", input.playerAccess, local_db_session
            )

            self.update_stage_attribute(
                stage.id, "config", input.config, local_db_session
            )
            local_db_session.commit()
            return convert_keys_to_camel_case(stage.to_dict())

    def update_stage_attribute(
        self, stage_id: int, name: str, value: str, local_db_session
    ):
        if not value:
            return

        if stage_id:
            stage_attribute = (
                local_db_session.query(StageAttributeModel)
                .filter(
                    and_(
                        StageAttributeModel.stage_id == stage_id,
                        StageAttributeModel.name == name,
                    )
                )
                .first()
            )
            if stage_attribute:
                stage_attribute.description = value
                local_db_session.commit()
                return
        local_db_session.add(
            StageAttributeModel(stage_id=stage_id, name=name, description=value)
        )

    def delete_stage(self, user: UserModel, id: int):
        with ScopedSession() as local_db_session:
            stage = (
                local_db_session.query(StageModel).filter(StageModel.id == id).first()
            )
            if not stage:
                raise GraphQLError("Stage not found")

            if stage.owner_id != user.id and user.role not in [ADMIN, SUPER_ADMIN]:
                raise GraphQLError("You are not authorized to delete this stage")

            local_db_session.query(StageAttributeModel).filter(
                StageAttributeModel.stage_id == id
            ).delete()
            local_db_session.query(ParentStageModel).filter(
                ParentStageModel.stage_id == id
            ).delete()

            local_db_session.query(SceneModel).filter(
                SceneModel.stage_id == id
            ).delete()

            performances = local_db_session.query(PerformanceModel).filter(
                PerformanceModel.stage_id == id
            )

            local_db_session.query(EventModel).filter(
                EventModel.performance_id.in_([p.id for p in performances])
            ).delete()

            local_db_session.query(PerformanceModel).filter(
                PerformanceModel.stage_id == id
            )

            local_db_session.delete(stage)
            local_db_session.commit()
            local_db_session.flush()
            return {"success": True, "message": "Stage deleted"}

    def duplicate_stage(self, user: UserModel, input: DuplicateStageInput):
        with ScopedSession() as local_db_session:
            stage = (
                local_db_session.query(StageModel)
                .filter(StageModel.id == input.id)
                .first()
            )
            if not stage:
                raise GraphQLError("Stage not found")

            file_location = self.get_short_name(input.name, local_db_session)

            new_stage = StageModel(
                name=input.name,
                description=stage.description,
                owner_id=user.id,
                file_location=file_location,
            )

            local_db_session.add(new_stage)
            local_db_session.commit()
            local_db_session.refresh(new_stage)

            self.copy_data(input, local_db_session, new_stage)

            local_db_session.commit()
            local_db_session.flush()
            return convert_keys_to_camel_case(new_stage.to_dict())

    def copy_data(
        self, input: DuplicateStageInput, local_db_session, new_stage: StageModel
    ):
        stage_attributes = (
            local_db_session.query(StageAttributeModel)
            .filter(StageAttributeModel.stage_id == input.id)
            .all()
        )

        for stage_attribute in stage_attributes:
            self.update_stage_attribute(
                new_stage.id,
                stage_attribute.name,
                stage_attribute.description,
                local_db_session,
            )

        parent_stages = (
            local_db_session.query(ParentStageModel)
            .filter(ParentStageModel.stage_id == input.id)
            .all()
        )
        for parent_stage in parent_stages:
            local_db_session.add(
                ParentStageModel(
                    stage_id=new_stage.id,
                    child_asset_id=parent_stage.child_asset_id,
                )
            )

    def get_short_name(self, name, local_db_session):
        shortname = re.sub(r"\s+", "-", re.sub("[^A-Za-z0-9 ]+", "", name)).lower()

        suffix = ""
        while True:
            existed_stage = (
                local_db_session.query(StageModel)
                .filter(StageModel.file_location == f"{shortname}{suffix}")
                .first()
            )
            if existed_stage:
                suffix = int(suffix or 0) + 1
            else:
                break
        return f"{shortname}{suffix}"

    def sweep_stage(self, user: UserModel, id: int):
        with ScopedSession() as local_db_session:
            stage = (
                local_db_session.query(StageModel).filter(StageModel.id == id).first()
            )
            if not stage:
                raise GraphQLError("Stage not found")

            events = (
                local_db_session.query(EventModel)
                .filter(EventModel.performance_id == None)
                .filter(EventModel.topic.ilike("%/{}/%".format(stage.file_location)))
            )

            if events.count() > 0:
                performance = PerformanceModel(stage_id=stage.id)

                local_db_session.add(performance)
                local_db_session.flush()

                events.update(
                    {EventModel.performance_id: performance.id},
                    synchronize_session="fetch",
                )
            else:
                raise GraphQLError("The stage is already sweeped!")

            local_db_session.commit()

            return convert_keys_to_camel_case(
                {"success": True, "performanceId": performance.id}
            )

    def update_status(self, user: UserModel, id: int):
        with ScopedSession() as local_db_session:
            stage = (
                local_db_session.query(StageModel).filter(StageModel.id == id).first()
            )
            if not stage:
                raise GraphQLError("Stage not found")

            if stage.owner_id != user.id and user.role not in [ADMIN, SUPER_ADMIN]:
                raise GraphQLError("You are not authorized to update this stage")

            attribute = (
                local_db_session.query(StageAttributeModel)
                .filter(
                    StageAttributeModel.stage_id == id,
                    StageAttributeModel.name == "status",
                )
                .first()
            )

            if attribute is not None:
                attribute.description = (
                    "rehearsal" if attribute.description == "live" else "live"
                )
            else:
                attribute = StageAttributeModel(
                    stage_id=id, name="status", description="live"
                )
            local_db_session.add(attribute)
            local_db_session.commit()
            return {"result": attribute.description}

    def update_visibility(self, user: UserModel, id: int):
        with ScopedSession() as local_db_session:
            stage = (
                local_db_session.query(StageModel).filter(StageModel.id == id).first()
            )
            if not stage:
                raise GraphQLError("Stage not found")

            if stage.owner_id != user.id and user.role not in [ADMIN, SUPER_ADMIN]:
                raise GraphQLError("You are not authorized to update this stage")

            attribute = (
                local_db_session.query(StageAttributeModel)
                .filter(
                    StageAttributeModel.stage_id == id,
                    StageAttributeModel.name == "visibility",
                )
                .first()
            )

            if attribute is not None:
                attribute.description = True if not attribute.description else ""
            else:
                attribute = StageAttributeModel(
                    stage_id=id, name="visibility", description=True
                )
            local_db_session.add(attribute)
            local_db_session.commit()
            return {"result": attribute.description}

    def update_last_access(self, user: UserModel, id: int):
        with ScopedSession() as local_db_session:
            stage = (
                local_db_session.query(StageModel).filter(StageModel.id == id).first()
            )
            if not stage:
                raise GraphQLError("Stage not found")

            if stage.owner_id != user.id and user.role not in [ADMIN, SUPER_ADMIN]:
                raise GraphQLError("You are not authorized to update this stage")

            stage.last_access = datetime.now()
            local_db_session.commit()
            return {"result": stage.last_access}

    def get_parent_stage(self):
        return [
            convert_keys_to_camel_case(stage.to_dict())
            for stage in DBSession.query(ParentStageModel).all()
        ]
