from config.settings import STREAM_EXPIRY_DAYS, STREAM_KEY
from datetime import datetime, timedelta
import hashlib
import json
from flask_jwt_extended import jwt_required, get_jwt_identity
from base64 import b64decode
import graphene
from graphql_relay.node.node import from_global_id
from graphene_sqlalchemy import SQLAlchemyObjectType
from asset.models import Asset as AssetModel, AssetType as AssetTypeModel
from config.project_globals import appdir, ScopedSession
import sys
import time
from flask_jwt_extended.view_decorators import verify_jwt_in_request
from graphene_sqlalchemy.fields import SQLAlchemyConnectionField
from sqlalchemy.sql.expression import and_, or_
from licenses.models import AssetLicense
import os
from user.models import ADMIN, SUPER_ADMIN
from user.user_utils import current_user
from performance_config.models import ParentStage
from utils.graphql_utils import CountableConnection, input_to_dictionary
import uuid
from sqlalchemy.orm import joinedload

appdir = os.path.abspath(os.path.dirname(__file__))
projdir = os.path.abspath(os.path.join(appdir, '..'))
if projdir not in sys.path:
    sys.path.append(appdir)
    sys.path.append(projdir)


absolutePath = os.path.dirname(appdir)
storagePath = 'ui/static/assets'


class AssetConnectionField(SQLAlchemyConnectionField):
    RELAY_ARGS = ['first', 'last', 'before', 'after']

    @classmethod
    def get_query(cls, model, info, sort=None, **args):
        query = super(AssetConnectionField, cls).get_query(
            model, info, sort, **args)

        result = verify_jwt_in_request(True)
        user_id = get_jwt_identity()
        query = query.filter(or_(
            AssetModel.asset_license == None,
            AssetModel.asset_license.has(AssetLicense.level < 3),
            and_(AssetModel.asset_license.has(AssetLicense.level == 3),
                 AssetModel.owner_id == user_id)
        ))
        for field, value in args.items():
            if field == 'id':
                _type, _id = from_global_id(value)
                query = query.filter(getattr(model, field) == _id)
            elif field == 'asset_type':
                query = query.filter(getattr(model, field).has(name=value))
            elif len(field) > 5 and field[-4:] == 'like':
                query = query.filter(
                    getattr(model, field[:-5]).ilike(f"%{value}%"))
            elif field not in cls.RELAY_ARGS and hasattr(model, field):
                query = query.filter(getattr(model, field) == value)
        return query


class AssignedStage(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    url = graphene.String()


class Asset(SQLAlchemyObjectType):
    db_id = graphene.Int(description="Database ID")
    src = graphene.String(description="Logical path of the media")
    stages = graphene.List(
        AssignedStage, description="Stages that this media is assigned to")
    copyright_level = graphene.Int(description="Copyright level")
    playerAccess = graphene.String(
        description="Users who can access and edit this media")
    permission = graphene.String(
        description="What permission the logged in user is granted to this media")
    sign = graphene.String(
        description="Stream sign that is required to publish from broadcaster")

    class Meta:
        model = AssetModel
        model.db_id = model.id
        interfaces = (graphene.relay.Node,)
        connection_class = CountableConnection

    def resolve_src(self, info):
        timestamp = int(time.mktime(self.updated_on.timetuple()))
        return self.file_location + '?t=' + str(timestamp)

    def resolve_stages(self, info):
        return [{'id': x.stage_id, 'name': x.stage.name, 'url': x.stage.file_location} for x in self.stages.all()]

    def resolve_copyright_level(self, info):
        if self.asset_license:
            return self.asset_license.level
        return 0

    def resolve_playerAccess(self, info):
        if self.asset_license and self.asset_license.permissions:
            return self.asset_license.permissions
        return "[]"

    def resolve_permission(self, info):
        result = verify_jwt_in_request(True)
        user_id = get_jwt_identity()
        if not user_id:
            return "none"
        if self.owner_id == user_id:
            return 'owner'
        if not self.asset_license or self.asset_license.level == 0:
            return "editor"
        if self.asset_license.level == 3:
            return "none"
        player_access = self.asset_license.permissions
        if player_access:
            accesses = json.loads(player_access)
            if len(accesses) == 2:
                if user_id in accesses[0]:
                    return "readonly"
                elif user_id in accesses[1]:
                    return "editor"
        return "none"

    def resolve_sign(self, info):
        result = verify_jwt_in_request(True)
        user_id = get_jwt_identity()
        if self.owner_id == user_id:
            timestamp = int((datetime.now() + timedelta(days=STREAM_EXPIRY_DAYS)).timestamp())
            payload = "/live/{0}-{1}-{2}".format(
                self.file_location, timestamp, STREAM_KEY)
            hashvalue = hashlib.md5(payload.encode('utf-8')).hexdigest()
            return "{0}-{1}".format(timestamp, hashvalue)
        return ''


class AssetType(SQLAlchemyObjectType):
    db_id = graphene.Int(description="Database ID")

    class Meta:
        model = AssetTypeModel
        model.db_id = model.id
        interfaces = (graphene.relay.Node,)


class UploadMedia(graphene.Mutation):
    """Mutation to upload a media."""
    asset = graphene.Field(
        lambda: Asset, description="Media uploaded by this mutation.")

    class Arguments:
        name = graphene.String(
            required=True, description="Name of the media")
        base64 = graphene.String(
            required=True, description="Base64 encoded content of the uploading media")
        media_type = graphene.String(
            description="Avatar/prop/backdrop,... default to just a generic media", default_value='media')
        filename = graphene.String(
            required=True, description="Original file name")

    @jwt_required()
    def mutate(self, info, name, base64, media_type, filename):
        current_user_id = get_jwt_identity()

        with ScopedSession() as local_db_session:
            asset_type = local_db_session.query(AssetTypeModel).filter(
                AssetTypeModel.name == media_type).first()
            if not asset_type:
                asset_type = AssetTypeModel(
                    name=media_type, file_location=media_type)
                local_db_session.add(asset_type)
                local_db_session.flush()

            # Save base64 to file
            filename, file_extension = os.path.splitext(filename)
            unique_filename = uuid.uuid4().hex + file_extension
            mediaDirectory = os.path.join(
                absolutePath, storagePath, asset_type.file_location)
            if not os.path.exists(mediaDirectory):
                os.makedirs(mediaDirectory)
            with open(os.path.join(mediaDirectory, unique_filename), "wb") as fh:
                fh.write(b64decode(base64.split(',')[1]))

            file_location = os.path.join(
                asset_type.file_location, unique_filename)
            asset = AssetModel(
                name=name,
                file_location=file_location,
                asset_type_id=asset_type.id,
                owner_id=current_user_id
            )
            local_db_session.add(asset)
            local_db_session.flush()
            local_db_session.commit()
            asset = local_db_session.query(AssetModel).options(joinedload(AssetModel.asset_type), joinedload(AssetModel.owner), joinedload(AssetModel.asset_license)).filter(
                AssetModel.id == asset.id).first()
            return UploadMedia(asset=asset)


class UpdateMedia(graphene.Mutation):
    """Mutation to upload a media."""
    asset = graphene.Field(
        lambda: Asset, description="Media updated by this mutation.")

    class Arguments:
        name = graphene.String(
            required=True, description="Name of the media")
        media_type = graphene.String(
            description="Avatar/prop/backdrop,... default to just a generic media", default_value='media')
        base64 = graphene.String(
            description="Base64 encoded content of the uploading media")
        file_location = graphene.String(description="File src")
        description = graphene.String(
            description="JSON serialized metadata of the media")
        id = graphene.ID(description="ID of the media")
        copyright_level = graphene.Int(description="Copyright level")
        player_access = graphene.String(
            description="Users who can access and edit this media")
        uploaded_frames = graphene.List(
            graphene.String, description="Base64 encoded of new uploaded frames")

    @jwt_required()
    def mutate(self, info, name, media_type, base64=None, file_location=None, description=None, id=None, copyright_level=None, player_access=None, uploaded_frames=None):
        current_user_id = get_jwt_identity()
        with ScopedSession() as local_db_session:
            asset_type = local_db_session.query(AssetTypeModel).filter(
                AssetTypeModel.name == media_type).first()
            if not asset_type:
                asset_type = AssetTypeModel(
                    name=media_type, file_location=media_type)
                local_db_session.add(asset_type)
                local_db_session.flush()

            if id:
                id = from_global_id(id)[1]
                asset = local_db_session.query(AssetModel).filter(
                    AssetModel.id == id).first()
            elif file_location:
                existedAsset = local_db_session.query(AssetModel).filter(
                    AssetModel.file_location == file_location).first()
                if existedAsset:
                    raise Exception(
                        "Media with the same key already existed, please pick another!")

                asset = AssetModel(owner_id=current_user_id)
                local_db_session.add(asset)

            if asset:
                asset.name = name
                asset.asset_type = asset_type
                asset.description = description
                if file_location:
                    if "?" in file_location:
                        file_location = file_location[:file_location.index(
                            "?")]
                    if asset.id and file_location != asset.file_location:
                        existedAsset = local_db_session.query(AssetModel).filter(
                            AssetModel.file_location == file_location).filter(AssetModel.id != asset.id).first()
                        if existedAsset:
                            raise Exception(
                                "Media with the same key already existed, please pick another!")
                    asset.file_location = file_location

                if base64:
                    # Replace image content
                    mediaDirectory = os.path.join(
                        absolutePath, storagePath, asset.file_location)
                    with open(mediaDirectory, "wb") as fh:
                        fh.write(b64decode(base64.split(',')[1]))
                    asset.updated_on = datetime.utcnow()

                if asset.asset_license:
                    asset.asset_license.level = copyright_level
                    asset.asset_license.permissions = player_access
                else:
                    if not asset.id:
                        local_db_session.flush()

                    asset_license = AssetLicense(
                        asset_id=asset.id,
                        level=copyright_level,
                        permissions=player_access
                    )
                    local_db_session.add(asset_license)
                local_db_session.flush()

            if uploaded_frames:
                filename, file_extension = os.path.splitext(
                    asset.file_location)
                attributes = json.loads(asset.description)
                if not attributes['frames']:
                    attributes['frames'] = []

                for frame in uploaded_frames:
                    unique_filename = uuid.uuid4().hex + file_extension
                    mediaDirectory = os.path.join(
                        absolutePath, storagePath, asset_type.file_location)
                    if not os.path.exists(mediaDirectory):
                        os.makedirs(mediaDirectory)
                    with open(os.path.join(mediaDirectory, unique_filename), "wb") as fh:
                        fh.write(b64decode(frame.split(',')[1]))

                    frame_location = os.path.join(
                        asset_type.file_location, unique_filename)
                    attributes['frames'].append(frame_location)

                asset.description = json.dumps(attributes)
                local_db_session.flush()

            local_db_session.flush()
            local_db_session.commit()
            asset = local_db_session.query(AssetModel).filter(
                AssetModel.id == asset.id).first()
            return UpdateMedia(asset=asset)


class DeleteMedia(graphene.Mutation):
    """Mutation to sweep a stage."""
    success = graphene.Boolean()
    message = graphene.String()

    class Arguments:
        id = graphene.ID(
            required=True, description="Global Id of the asset to be deleted.")

    @jwt_required()
    def mutate(self, info, id):
        with ScopedSession() as local_db_session:
            id = from_global_id(id)[1]
            asset = local_db_session.query(AssetModel).filter(
                AssetModel.id == id).first()
            if asset:
                code, error, user, timezone = current_user()
                if not user.role in (ADMIN, SUPER_ADMIN):
                    if not user.id == asset.owner_id:
                        return DeleteMedia(success=False, message="Only media owner or admin can delete this media!")

                attributes = json.loads(asset.description)
                # Delete frames that was assigned only to this media
                for frame in attributes['frames']:
                    frame_asset = local_db_session.query(AssetModel).filter(
                        AssetModel.file_location == frame).first()
                    if not frame_asset:
                        physical_path = os.path.join(
                            absolutePath, storagePath, frame)
                        if os.path.exists(physical_path):
                            os.remove(physical_path)

                physical_path = os.path.join(
                    absolutePath, storagePath, asset.file_location)
                local_db_session.query(ParentStage).filter(
                    ParentStage.child_asset_id == id).delete(synchronize_session=False)
                local_db_session.query(AssetLicense).filter(
                    AssetLicense.asset_id == id).delete(synchronize_session=False)

                for multiframe_media in local_db_session.query(AssetModel).filter(AssetModel.description.like(f"%{asset.file_location}%")).all():
                    attributes = json.loads(multiframe_media.description)
                    attributes['frames'].remove(asset.file_location)
                    multiframe_media.description = json.dumps(attributes)
                    local_db_session.commit()

                local_db_session.delete(asset)
                local_db_session.flush()
                local_db_session.commit()
            else:
                return DeleteMedia(success=False, message="Media not found!")

            if os.path.exists(physical_path):
                os.remove(physical_path)
            else:
                return DeleteMedia(success=True, message="Media deleted successfully but file not existed on storage!")

        return DeleteMedia(success=True, message="Media deleted successfully!")


class AssignStagesInput(graphene.InputObjectType):
    id = graphene.ID(required=True, description="Global Id of the media.")
    stage_ids = graphene.List(
        graphene.Int, description="Id of stages to be assigned to")


class AssignStages(graphene.Mutation):
    """Mutation to assign stages to a media."""
    asset = graphene.Field(
        lambda: Asset, description="Asset with assigned stages")

    class Arguments:
        input = AssignStagesInput(required=True)

    # decorate this with jwt login decorator.
    def mutate(self, info, input):
        data = input_to_dictionary(input)
        with ScopedSession() as local_db_session:
            asset = local_db_session.query(AssetModel).filter(
                AssetModel.id == data['id']
            ).first()
            asset.stages.delete()
            for id in data['stage_ids']:
                asset.stages.append(ParentStage(stage_id=id))

            local_db_session.flush()
            local_db_session.commit()

            asset = local_db_session.query(AssetModel).filter(
                AssetModel.id == data['id']).first()

            return AssignStages(asset=asset)
