from base64 import b64decode
import json
import os
import uuid
from graphql import GraphQLError
from sqlalchemy import and_, or_
from assets.db_models.asset import AssetModel
from assets.db_models.asset_license import AssetLicenseModel
from assets.db_models.asset_type import AssetTypeModel
from assets.db_models.asset_usage import AssetUsageModel
from assets.db_models.media_tag import MediaTagModel
from assets.services.asset import AssetService
from assets.services.asset_license import AssetLicenseService
from global_config import (
    DBSession,
    ScopedSession,
    convert_keys_to_camel_case,
)
from files.file_handling import FileHandling
from stages.db_models.parent_stage import ParentStageModel
from stages.db_models.stage import StageModel
from stages.http.validation import (
    AssignMediaInput,
    AssignStagesInput,
    UpdateMediaInput,
    UploadMediaInput,
)
from users.db_models.user import UserModel

appdir = os.path.abspath(os.path.dirname(__file__))
absolutePath = os.path.dirname(os.path.abspath(os.path.join(appdir, "..", "..")))
storagePath = "uploads/assets"


class MediaService:
    def __init__(self):
        self.asset_service = AssetService()
        self.asset_license_service = AssetLicenseService()
        self.file_handling = FileHandling()

    def assign_media(self, input: AssignMediaInput):
        with ScopedSession() as local_db_session:
            stage = local_db_session.query(StageModel).filter_by(id=input.id).first()
            if not stage or not input.id:
                raise GraphQLError("Stage not found")

            local_db_session.query(ParentStageModel).filter(
                ParentStageModel.stage_id == input.id
            ).delete()

            for media_id in input.mediaIds:
                media = ParentStageModel(stage_id=input.id, child_asset_id=media_id)
                local_db_session.add(media)

            local_db_session.flush()
            return convert_keys_to_camel_case(stage.to_dict())

    def upload_media(self, user: UserModel, input: UploadMediaInput):
        with ScopedSession() as local_db_session:
            asset_type = self.asset_service.validate_asset_type(input, local_db_session)
            file_location = self.file_handling.upload_file(
                base64=input.base64,
                file_name=input.filename,
                absolute_path=absolutePath,
                storage_path=storagePath,
                sub_path=asset_type.file_location,
            )

            asset = self.asset_service.create_asset(
                owner=user,
                asset_type_id=asset_type.id,
                name=input.name,
                file_location=file_location,
                local_db_session=local_db_session,
            )

            return self.asset_service.resolve_fields(asset)

    def update_media(self, input: UpdateMediaInput):
        asset = None
        with ScopedSession() as local_db_session:
            asset_type = self.asset_service.validate_asset_type(input, local_db_session)

            asset = self.retrieve_asset(input, local_db_session)
            asset.name = input.name
            asset.asset_type_id = asset_type.id
            asset.description = input.description

            file_location = self.asset_service.process_file_location(
                {"urls": [input.fileLocation]}, local_db_session, asset
            )
            asset.file_location = file_location

            if input.base64:
                self.file_handling.write_file(
                    base64=input.base64,
                    path=os.path.join(absolutePath, storagePath, asset.file_location),
                )

            self.asset_license_service.create(
                asset_id=asset.id,
                player_access=input.playerAccess,
                local_db_session=local_db_session,
                copyright_level=input.copyrightLevel,
            )
            asset.description = self.process_uploaded_frames(input, asset, asset_type)
            local_db_session.commit()
            local_db_session.flush()
            asset = DBSession.query(AssetModel).filter_by(id=asset.id).first()
            return convert_keys_to_camel_case(asset.to_dict())

    def retrieve_asset(self, input, local_db_session):
        if input.id:
            asset = local_db_session.query(AssetModel).filter_by(id=input.id).first()
            if not asset:
                raise GraphQLError("Media not found")

        if input.fileLocation:
            existed_asset = (
                local_db_session.query(AssetModel)
                .filter(
                    and_(
                        AssetModel.file_location == input.fileLocation,
                        AssetModel.id != input.id,
                    )
                )
                .first()
            )
            if existed_asset:
                raise GraphQLError(
                    "Media with the same key already existed, please pick another!"
                )

        return asset

    def process_uploaded_frames(
        self, input: UpdateMediaInput, asset: AssetModel, asset_type: AssetTypeModel
    ):
        if input.uploadedFrames:
            filename, file_extension = os.path.splitext(asset.file_location)
            attributes = json.loads(asset.description)
            if "frames" not in attributes:
                attributes["frames"] = []

            for frame in input.uploadedFrames:
                filename = uuid.uuid4().hex + file_extension

                frame_location = self.file_handling.upload_file(
                    base64=frame,
                    file_name=filename,
                    absolute_path=absolutePath,
                    storage_path=storagePath,
                    sub_path=asset_type.file_location,
                )

                frame_location = os.path.join(asset_type.file_location, filename)
                attributes["frames"].append(frame_location)

            return json.dumps(attributes)

    def delete_media(self, id: int):
        with ScopedSession() as local_db_session:
            asset = local_db_session.query(AssetModel).filter_by(id=id).first()
            if not asset:
                raise GraphQLError("Media not found")
            physical_path = self.remove_media_frames_and_get_path(
                local_db_session, asset
            )

            self.file_handling.delete_file(physical_path)

            self.cleanup_related_entities(id, local_db_session)
            self.remove_asset_from_frames(local_db_session, asset)
            local_db_session.delete(asset)
            return {"success": True, "message": "Media deleted successfully"}

    def remove_media_frames_and_get_path(self, local_db_session, asset):
        if asset.description:
            attributes = json.loads(asset.description)
            if "frames" in attributes and attributes["frames"]:
                self._delete_frames(local_db_session, attributes["frames"])
        return self._get_physical_path(asset.file_location)

    def _delete_frames(self, local_db_session, frames):
        for frame in frames:
            frame_asset = (
                local_db_session.query(AssetModel)
                .filter(
                    or_(
                        AssetModel.file_location == frame,
                        AssetModel.description.contains(frame),
                    )
                )
                .first()
            )
            if not frame_asset:
                self.file_handling.delete_file( os.path.join(absolutePath, storagePath, frame))

    def _get_physical_path(self, file_location):
        return os.path.join(absolutePath, storagePath, file_location)

    def cleanup_related_entities(self, id: int, local_db_session):
        local_db_session.query(ParentStageModel).filter(
            ParentStageModel.child_asset_id == id
        ).delete(synchronize_session=False)
        local_db_session.query(MediaTagModel).filter(
            MediaTagModel.asset_id == id
        ).delete(synchronize_session=False)
        local_db_session.query(AssetLicenseModel).filter(
            AssetLicenseModel.asset_id == id
        ).delete(synchronize_session=False)
        local_db_session.query(AssetUsageModel).filter(
            AssetUsageModel.asset_id == id
        ).delete(synchronize_session=False)

    def remove_asset_from_frames(self, local_db_session, asset: AssetModel):
        for multiple_frame_media in (
            local_db_session.query(AssetModel)
            .filter(AssetModel.description.ilike(f"%{asset.file_location}%"))
            .all()
        ):
            attributes = json.loads(multiple_frame_media.description)
            for i, frame in enumerate(attributes["frames"]):
                if "?" in frame:
                    attributes["frames"][i] = frame[: frame.index("?")]
            if asset.file_location in attributes["frames"]:
                attributes["frames"].remove(asset.file_location)
            multiple_frame_media.description = json.dumps(attributes)
            local_db_session.flush()

    def assign_stages(self, input: AssignStagesInput):
        with ScopedSession() as local_db_session:
            local_db_session.query(ParentStageModel).filter(
                ParentStageModel.child_asset_id == input.id
            ).delete()
            for stage_id in input.stageIds:
                local_db_session.add(
                    ParentStageModel(stage_id=stage_id, child_asset_id=input.id)
                )
            local_db_session.flush()

            asset = local_db_session.query(AssetModel).filter_by(id=input.id).first()
            return convert_keys_to_camel_case(asset.to_dict())
