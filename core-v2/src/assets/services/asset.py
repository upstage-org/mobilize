from base64 import b64decode
from datetime import datetime, timedelta
import hashlib
import json
from operator import or_
import os
from typing import Optional
import uuid
import time
from graphql import GraphQLError


from global_config import (
    ScopedSession,
    DBSession,
    STREAM_EXPIRY_DAYS,
    STREAM_KEY,
    convert_keys_to_camel_case,
)
from assets.db_models.asset import AssetModel, AvatarVoice, Voice
from assets.db_models.asset_license import AssetLicenseModel
from assets.db_models.asset_type import AssetTypeModel
from assets.db_models.asset_usage import AssetUsageModel
from assets.db_models.media_tag import MediaTagModel
from assets.db_models.tag import TagModel
from assets.http.validation import MediaTableInput, SaveMediaInput
from stages.db_models.parent_stage import ParentStageModel
from users.db_models.user import ADMIN, SUPER_ADMIN, UserModel
from files.file_handling import FileHandling


appdir = os.path.abspath(os.path.dirname(__file__))
absolutePath = os.path.dirname(appdir)
storagePath = "../../uploads/assets"


class AssetService:
    def __init__(self):
        self.file_handing = FileHandling()
        pass

    def get_all_medias(self, user: UserModel, filter: dict = None):
        query = (
            DBSession.query(AssetModel)
            .join(AssetTypeModel)
            .join(UserModel)
            .outerjoin(AssetLicenseModel)
        )

        if "mediaType" in filter:
            query = query.filter(AssetTypeModel.name == filter["mediaType"])

        if "owner" in filter:
            query = query.filter(UserModel.username == filter["owner"])

        assets = query.all()

        return [self.resolve_fields(asset, user) for asset in assets]

    def search_assets(self, search_assets: MediaTableInput):
        total_count = DBSession.query(AssetModel).count()

        query = (
            DBSession.query(AssetModel)
            .join(UserModel)
            .join(AssetTypeModel)
            .outerjoin(AssetLicenseModel)
        )
        if search_assets.name:
            query = query.filter(AssetModel.name.like(f"%{search_assets.name}%"))
        if search_assets.mediaTypes:
            query = query.filter(AssetTypeModel.name.in_(search_assets.mediaTypes))
        if search_assets.owners:
            query = query.filter(UserModel.username.in_(search_assets.owners))

        if search_assets.stages:
            query = query.filter(
                AssetModel.stages.any(
                    ParentStageModel.stage_id.in_(search_assets.stages)
                )
            )
        if search_assets.tags:
            query = (
                query.join(MediaTagModel)
                .join(TagModel)
                .filter(TagModel.name.in_(search_assets.tags))
            )
        if search_assets.createdBetween:
            query = query.filter(
                AssetModel.created_on.between(
                    search_assets.createdBetween[0], search_assets.createdBetween[1]
                )
            )

        if search_assets.sort:
            sort = search_assets.sort
            for sort_option in sort:
                field, direction = sort_option.rsplit("_", 1)
                if field == "ASSET_TYPE_ID":
                    sort_field = AssetModel.asset_type_id
                elif field == "OWNER_ID":
                    sort_field = AssetModel.owner_id
                elif field == "NAME":
                    sort_field = AssetModel.name
                elif field == "CREATED_ON":
                    sort_field = AssetModel.created_on

                if direction == "ASC":
                    query = query.order_by(sort_field.asc())
                elif direction == "DESC":
                    query = query.order_by(sort_field.desc())
        if search_assets.page and search_assets.limit:
            query = query.limit(search_assets.limit).offset(
                (search_assets.page - 1) * search_assets.limit
            )
        
        assets = query.all()

        return {
            "totalCount": total_count,
            "edges": [convert_keys_to_camel_case(asset.to_dict()) for asset in assets],
        }

    def upload_file(self, base64: str, filename: str):
        file_location = self.file_handing.upload_file(
            base64, filename, absolutePath, storagePath, "media"
        )
        return {"url": file_location}

    def save_media(self, owner: UserModel, input: SaveMediaInput):
        asset = None
        with ScopedSession() as local_db_session:
            asset_type = self.validate_asset_type(input, local_db_session)

            if input.id:
                asset = (
                    local_db_session.query(AssetModel)
                    .filter(AssetModel.id == input.id)
                    .first()
                )
                if (
                    owner.role not in [SUPER_ADMIN, ADMIN]
                    and asset.owner_id != owner.id
                ):
                    raise GraphQLError("You are not allowed to update this asset")
            else:
                asset = AssetModel(owner_id=owner.id)
                local_db_session.add(asset)

            asset.name = input.name
            asset.asset_type_id = asset_type.id
            asset.copyright_level = input.copyrightLevel
            file_location = self.process_file_location(input, local_db_session, asset)

            self.change_owner(owner, local_db_session, asset)

            self.process_urls(input, local_db_session, asset_type, asset, file_location)

            self.update_asset_permissions(input, local_db_session, asset)
            asset = self.update_asset_tags(input, local_db_session, asset)
            local_db_session.commit()
            local_db_session.flush()

            return convert_keys_to_camel_case({"asset": {"id": asset.id}})

    def update_asset_tags(
        self, input: SaveMediaInput, local_db_session, asset: AssetModel
    ):
        if input.tags:
            tags = input.tags
            asset.tags.delete()
            for tag in tags:
                tag_model = (
                    local_db_session.query(TagModel)
                    .filter(TagModel.name == tag)
                    .first()
                )
                if not tag_model:
                    tag_model = TagModel(name=tag)
                    local_db_session.add(tag_model)
                    local_db_session.flush()
                asset.tags.append(MediaTagModel(tag_id=tag_model.id))

            local_db_session.flush()
            asset = (
                local_db_session.query(AssetModel)
                .filter(AssetModel.id == asset.id)
                .first()
            )

        return asset

    def create_asset(
        self,
        owner: UserModel,
        asset_type_id: int,
        name: str,
        file_location: str,
        local_db_session,
    ):
        asset = AssetModel(
            owner_id=owner.id,
            asset_type_id=asset_type_id,
            name=name,
            file_location=file_location,
        )
        local_db_session.add(asset)
        local_db_session.flush()
        local_db_session.refresh(asset)
        return asset

    def update_asset_permissions(
        self, input: SaveMediaInput, local_db_session, asset: AssetModel
    ):
        if input.userIds:
            user_ids = input.userIds
            granted_permissions = asset.permissions.all()
            for permission in granted_permissions:
                if isinstance(permission, AssetUsageModel):
                    if (
                        permission.user_id not in user_ids
                        and permission.approved == True
                    ):
                        asset.permissions.remove(permission)
                        local_db_session.delete(permission)
            for user_id in user_ids:
                permission = (
                    local_db_session.query(AssetUsageModel)
                    .filter(
                        AssetUsageModel.asset_id == asset.id,
                        AssetUsageModel.user_id == user_id,
                    )
                    .first()
                )
                if not permission:
                    permission = AssetUsageModel(user_id=user_id)
                    asset.permissions.append(permission)
                permission.approved = True
            local_db_session.flush()

    def process_urls(
        self,
        input: SaveMediaInput,
        local_db_session,
        asset_type: AssetTypeModel,
        asset: AssetModel,
        file_location: str,
    ):
        if input.urls:
            urls = input.urls
            if not asset.description:
                asset.description = "{}"

            attributes = json.loads(asset.description)

            if not "frames" in attributes or attributes["frames"]:
                attributes["frames"] = []

            asset.size = 0
            for url in urls:
                attributes["frames"].append(url)
                full_path = os.path.join(absolutePath, storagePath, url)
                try:
                    size = os.path.getsize(full_path)
                except:
                    size = 0  # file not exist
                asset.size += size

            attributes["multi"] = True if len(urls) > 0 else False
            attributes["frames"] = attributes["frames"] if len(urls) > 0 else []
            attributes["w"] = input.w
            attributes["h"] = input.h
            if asset_type.name == "stream" and "/" not in file_location:
                attributes["isRTMP"] = True

            if "voice" in input:
                voice = input["voice"]
                if voice and voice.voice:
                    attributes["voice"] = voice
                elif "voice" in attributes:
                    del attributes["voice"]

            if "link" in input:
                link = input["link"]
                if link and link.url:
                    attributes["link"] = link
                elif "link" in attributes:
                    del attributes["link"]

            attributes["note"] = input.note
            asset.description = json.dumps(attributes)
            local_db_session.flush()
        if input.stageIds != None:
            asset.stages = []
            for id in input.stageIds:
                asset.stages.append(ParentStageModel(stage_id=id))

    def change_owner(self, owner: UserModel, local_db_session, asset: AssetModel):
        if owner:
            new_owner = (
                local_db_session.query(UserModel)
                .filter(UserModel.username == owner.username)
                .first()
            )
            if new_owner:
                if new_owner.id != asset.owner_id and owner.role in (
                    ADMIN,
                    SUPER_ADMIN,
                ):
                    asset.owner_id = new_owner.id
            else:
                raise GraphQLError("Owner not found")
        asset.updated_on = datetime.now()
        local_db_session.flush()

    def process_file_location(self, input, local_db_session, asset):
        file_location = input["urls"][0] if "urls" in input else input.urls[0]
        asset.file_location = uuid.uuid4()
        if "?" in file_location:
            file_location = file_location[: file_location.index("?")]
            if file_location != asset.file_location and "/" not in file_location:
                existed_asset = (
                    local_db_session.query(AssetModel)
                    .filter(AssetModel.file_location == file_location)
                    .filter(AssetModel.id != asset.id)
                    .first()
                )
                if existed_asset:
                    raise GraphQLError(
                        "Stream with the same key already existed, please pick another unique key!"
                    )
            asset.file_location = file_location

        return file_location

    def validate_asset_type(self, input, local_db_session):
        media_type = input.mediaType
        asset_type = (
            local_db_session.query(AssetTypeModel)
            .filter(AssetTypeModel.name == media_type)
            .first()
        )

        if not asset_type:
            asset_type = AssetTypeModel(name=media_type, file_location=media_type)
            local_db_session.add(asset_type)
            local_db_session.flush()

        return asset_type

    def delete_media(self, owner: UserModel, id: int):
        with ScopedSession() as local_db_session:
            asset = (
                local_db_session.query(AssetModel).filter(AssetModel.id == id).first()
            )

            if not asset:
                raise GraphQLError("Media not found")

            if owner.role not in (ADMIN, SUPER_ADMIN) and owner.id != asset.owner_id:
                return {
                    "success": False,
                    "message": "Only media owner or admin can delete this media!",
                }

            self.cleanup_assets(local_db_session, asset)
            local_db_session.delete(asset)
            local_db_session.flush()

            return {
                "success": True,
                "message": "Media deleted successfully!",
            }

    def cleanup_assets(self, local_db_session, asset: AssetModel):
        if asset.description:
            attributes = json.loads(asset.description)
            if "frames" in attributes:
                for frame in attributes["frames"]:
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
                        self.file_handing.delete_file(
                            os.path.join(absolutePath, storagePath, frame)
                        )

        physical_path = os.path.join(absolutePath, storagePath, asset.file_location)
        local_db_session.query(ParentStageModel).filter(
            ParentStageModel.child_asset_id == asset.id
        ).delete(synchronize_session=False)
        local_db_session.query(MediaTagModel).filter(
            MediaTagModel.asset_id == asset.id
        ).delete(synchronize_session=False)
        local_db_session.query(AssetLicenseModel).filter(
            AssetLicenseModel.asset_id == asset.id
        ).delete(synchronize_session=False)
        local_db_session.query(AssetUsageModel).filter(
            AssetUsageModel.asset_id == asset.id
        ).delete(synchronize_session=False)

        for multiframe_media in (
            local_db_session.query(AssetModel)
            .filter(AssetModel.description.like(f"%{asset.file_location}%"))
            .all()
        ):
            attributes = json.loads(multiframe_media.description)
            for i, frame in enumerate(attributes["frames"]):
                if "?" in frame:
                    attributes["frames"][i] = frame[: frame.index("?")]
            if asset.file_location in attributes["frames"]:
                attributes["frames"].remove(asset.file_location)
            multiframe_media.description = json.dumps(attributes)
            local_db_session.flush()

        self.file_handing.delete_file(physical_path)

    def resolve_sign(self, user: UserModel, asset: AssetModel):
        if asset.owner_id == user.id:
            timestamp = int(
                (datetime.now() + timedelta(days=STREAM_EXPIRY_DAYS)).timestamp()
            )
            payload = "/live/{0}-{1}-{2}".format(
                asset.file_location, timestamp, STREAM_KEY
            )
            hashvalue = hashlib.md5(payload.encode("utf-8")).hexdigest()
            return "{0}-{1}".format(timestamp, hashvalue)
        return ""

    def resolve_src(self, asset: AssetModel):
        timestamp = int(time.mktime(asset.updated_on.timetuple()))
        return asset.file_location + "?t=" + str(timestamp)

    def resolve_permissions(self, user_id: int, asset: AssetModel):
        if not user_id:
            return "none"
        if asset.owner_id == user_id:
            return "owner"
        if not asset.asset_license or asset.asset_license.level == 0:
            return "editor"
        if asset.asset_license.level == 3:
            return "none"

        player_access = asset.asset_license.permissions if asset.asset_license else None
        if player_access:
            accesses = json.loads(player_access)
            if len(accesses) == 2:
                if user_id in accesses[0]:
                    return "readonly"
                elif user_id in accesses[1]:
                    return "editor"
        return "none"

    def resolve_fields(self, asset: AssetModel, user: Optional[UserModel] = None):
        src = self.resolve_src(asset)
        sign = self.resolve_sign(asset.owner, asset)
        user_id = user.id if user else asset.owner_id
        permission = self.resolve_permissions(user_id, asset)
        return {
            **convert_keys_to_camel_case(asset.to_dict()),
            "src": src,
            "sign": sign,
            "permission": permission,
        }

    def get_media_types(self):
        return [
            convert_keys_to_camel_case(type.to_dict())
            for type in DBSession.query(AssetTypeModel).all()
        ]

    def get_tags(self):
        return [
            convert_keys_to_camel_case(tag.to_dict())
            for tag in DBSession.query(TagModel).all()
        ]

    def get_voices(self):
        voices = []
        for media in (
            DBSession.query(AssetModel)
            .filter(AssetModel.asset_type.has(AssetTypeModel.name == "avatar"))
            .all()
        ):
            if media.description:
                attributes = json.loads(media.description)
                if "voice" in attributes:
                    voice = attributes["voice"]
                    if voice and voice["voice"]:
                        av = AvatarVoice()
                        av.voice = voice["voice"]
                        av.variant = voice["variant"]
                        for key in ["pitch", "speed", "amplitude"]:
                            if key in voice:
                                setattr(av, key, int(voice[key]))
                            else:
                                if key == "speed":
                                    setattr(av, key, 175)
                                else:
                                    setattr(av, key, 50)
                        voices.append(Voice(avatar=media, voice=av))
        return [convert_keys_to_camel_case(voice) for voice in voices]
