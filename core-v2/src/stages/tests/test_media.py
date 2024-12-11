import pytest
from assets.db_models.asset import AssetModel
from authentication.tests.auth_test import TestAuthenticationController
from global_config import DBSession
from stages.tests.test_stage import TestStageController
from assets.tests.asset_test import TestAssetController, load_base64_from_image
from src.main import app
from stages.http.schema import stage_graphql_app
from users.db_models.user import SUPER_ADMIN
import random

app.mount("/stage_graphql", stage_graphql_app)
test_AuthenticationController = TestAuthenticationController()
test_StageController = TestStageController()
test_AssetController = TestAssetController()


@pytest.mark.anyio
class TestMediaController:
    async def assign_media(self, client, stage_id, media_ids):
        headers = test_AuthenticationController.get_headers(client, SUPER_ADMIN)
        variables = {"input": {"id": stage_id, "mediaIds": media_ids}}

        query = """
            mutation assignMedia($input: AssignMediaInput!) {
                assignMedia(input: $input) {
                    id
                    }
                }
        """

        response = client.post(
            "/stage_graphql",
            json={"query": query, "variables": variables},
            headers=headers,
        )
        assert response.status_code == 200
        return response

    async def test_01_assign_media(self, client):
        stage = await test_StageController.test_01_create_stage(client)
        await test_AssetController.test_03_save_media_successfully(client)
        assets = DBSession.query(AssetModel).all()
        response = await self.assign_media(
            client, stage["id"], [asset.id for asset in assets]
        )

        assert "data" in response.json()
        assert "assignMedia" in response.json()["data"]
        assert "id" in response.json()["data"]["assignMedia"]
        assert "errors" not in response.json()
        assert response.json()["data"]["assignMedia"]["id"] == stage["id"]

    async def test_02_assign_media_stage_not_found(self, client):
        assets = DBSession.query(AssetModel).all()
        response = await self.assign_media(client, 0, [asset.id for asset in assets])
        data = response.json()
        assert "errors" in data
        assert data["errors"][0]["message"] == "Stage not found"

    async def test_03_upload_media(self, client):
        headers = test_AuthenticationController.get_headers(client, SUPER_ADMIN)

        variables = {
            "input": {
                "name": "test",
                "mediaType": "image",
                "filename": "test.png",
                "base64": f"data:image/jpeg;base64,{load_base64_from_image('src/assets/tests/images/test.png')}",
            }
        }

        query = """
            mutation uploadMedia($input: UploadMediaInput!) {
                uploadMedia(input: $input) {
                    id
                    }
                }
        """

        response = client.post(
            "/stage_graphql",
            json={"query": query, "variables": variables},
            headers=headers,
        )

        assert response.status_code == 200
        assert "data" in response.json()
        assert "uploadMedia" in response.json()["data"]
        assert "id" in response.json()["data"]["uploadMedia"]
        assert "errors" not in response.json()
        return response.json()["data"]["uploadMedia"]["id"]

    async def test_04_update_media(self, client):
        headers = test_AuthenticationController.get_headers(client, SUPER_ADMIN)
        await test_AssetController.test_03_save_media_successfully(client)
        asset = DBSession.query(AssetModel).first()
        file_location = f"image/test{random.randint(1, 1000)}.png"
        response = self.update_media(client, headers, asset.id, file_location)
        assert response.status_code == 200
        assert "data" in response.json()
        assert "updateMedia" in response.json()["data"]
        assert "id" in response.json()["data"]["updateMedia"]
        assert "errors" not in response.json()

        response = self.update_media(client, headers, 1000)
        assert response.status_code == 200
        assert "errors" in response.json()

        asset = DBSession.query(AssetModel).all()[1]
        response = self.update_media(client, headers, asset.id, file_location)
        assert "errors" in response.json()

    def update_media(self, client, headers, id, file_location="image/test.png"):
        variables = {
            "input": {
                "id": id,
                "name": "updated_test",
                "mediaType": "image",
                "description": '{ "config": "test" }',
                "fileLocation": file_location,
                "base64": f"data:image/jpeg;base64,{load_base64_from_image('src/assets/tests/images/test.png')}",
                "copyrightLevel": 2,
                "playerAccess": "public",
                "uploadedFrames": [
                    f"data:image/jpeg;base64,{load_base64_from_image('src/assets/tests/images/test.png')}"
                ],
            }
        }

        query = """
            mutation updateMedia($input: UpdateMediaInput!) {
                updateMedia(input: $input) {
                    id
                    }
                }
        """

        response = client.post(
            "/stage_graphql",
            json={"query": query, "variables": variables},
            headers=headers,
        )
        return response

    async def test_05_delete_media(self, client):
        headers = test_AuthenticationController.get_headers(client, SUPER_ADMIN)
        asset = DBSession.query(AssetModel).first()
        self.update_media(
            client, headers, asset.id, f"image/test{random.randint(1, 1000)}.png"
        )

        response = self.delete_media_request(client, headers, asset)
        assert response.json()["data"]["deleteMediaOnStage"]["success"] == True

    async def test_06_delete_media_not_found(self, client):
        headers = test_AuthenticationController.get_headers(client, SUPER_ADMIN)
        response = self.delete_media_request(client, headers, AssetModel(id=0))
        assert "errors" in response.json()
        assert response.json()["errors"][0]["message"] == "Media not found"

    def delete_media_request(self, client, headers, asset):
        variables = {"id": asset.id}

        query = """
            mutation deleteMediaOnStage($id: ID!) {
                deleteMediaOnStage(id: $id) {
                        success
                    }
                }
        """

        response = client.post(
            "/stage_graphql",
            json={"query": query, "variables": variables},
            headers=headers,
        )

        assert response.status_code == 200
        assert "data" in response.json()
        assert "deleteMediaOnStage" in response.json()["data"]
        return response

    async def assign_stages(self, client, headers, stage_ids, media_id):
        variables = {"input": {"stageIds": stage_ids, "id": media_id}}

        query = """
            mutation assignStages($input: AssignStagesInput!) {
                assignStages(input: $input) {
                        id
                    }
                }
        """

        response = client.post(
            "/stage_graphql",
            json={"query": query, "variables": variables},
            headers=headers,
        )
        return response

    async def test_07_assign_stages(self, client):
        headers = test_AuthenticationController.get_headers(client, SUPER_ADMIN)
        stage = await test_StageController.test_01_create_stage(client)
        stage2 = await test_StageController.test_01_create_stage(client)
        asset = DBSession.query(AssetModel).first()

        response = await self.assign_stages(
            client, headers, [stage["id"], stage2["id"]], asset.id
        )
        assert response.json()["data"]["assignStages"]["id"] is not None
