import os
from user.models import ADMIN, SUPER_ADMIN
from user.user_utils import current_user
from performance_config.models import ParentStage
from utils.graphql_utils import CountableConnection, input_to_dictionary
import uuid

from sqlalchemy.orm import joinedload

from config.project_globals import appdir, ScopedSession
from asset.models import Asset as AssetModel, AssetType as AssetTypeModel
from graphene_sqlalchemy import SQLAlchemyObjectType
from graphql_relay.node.node import from_global_id
import graphene
from base64 import b64decode
from flask_jwt_extended import jwt_required, get_jwt_identity

absolutePath = os.path.dirname(appdir)
storagePath = 'ui/static/assets'


class AssignedStage(graphene.ObjectType):
    id = graphene.Int()
    name = graphene.String()
    url = graphene.String()


class Asset(SQLAlchemyObjectType):
    db_id = graphene.Int(description="Database ID")
    stages = graphene.List(
        AssignedStage, description="Stages that this media is assigned to")

    class Meta:
        model = AssetModel
        model.db_id = model.id
        interfaces = (graphene.relay.Node,)
        connection_class = CountableConnection

    def resolve_stages(self, info):
        if not self.stages:
            return []
        return [{'id': x.stage_id, 'name': x.stage.name, 'url': x.stage.file_location} for x in self.stages.all()]


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
            asset = local_db_session.query(AssetModel).options(joinedload(AssetModel.asset_type), joinedload(AssetModel.owner)).filter(
                AssetModel.id == asset.id).first()
            return UploadMedia(asset=asset)


class UpdateMedia(graphene.Mutation):
    """Mutation to upload a media."""
    asset = graphene.Field(
        lambda: Asset, description="Media updated by this mutation.")

    class Arguments:
        id = graphene.ID(
            required=True, description="ID of the media")
        name = graphene.String(
            required=True, description="Name of the media")
        media_type = graphene.String(
            description="Avatar/prop/backdrop,... default to just a generic media", default_value='media')
        description = graphene.String(
            description="JSON serialized metadata of the media")

    def mutate(self, info, id, name, media_type, description):
        with ScopedSession() as local_db_session:
            asset_type = local_db_session.query(AssetTypeModel).filter(
                AssetTypeModel.name == media_type).first()
            if not asset_type:
                asset_type = AssetTypeModel(
                    name=media_type, file_location=media_type)
                local_db_session.add(asset_type)
                local_db_session.flush()

            id = from_global_id(id)[1]
            asset = local_db_session.query(AssetModel).filter(
                AssetModel.id == id).first()
            if asset:
                asset.name = name
                asset.asset_type = asset_type
                asset.description = description

            local_db_session.flush()
            local_db_session.commit()
            asset = local_db_session.query(AssetModel).filter(
                AssetModel.id == asset.id).first()
            return UploadMedia(asset=asset)


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

                physical_path = os.path.join(
                    absolutePath, storagePath, asset.file_location)
                local_db_session.query(ParentStage).filter(
                    ParentStage.child_asset_id == id).delete(synchronize_session=False)
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
    """Mutation to update a stage."""
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
