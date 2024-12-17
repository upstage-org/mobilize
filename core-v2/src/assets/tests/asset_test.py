import base64
import pytest
from src.main import app
from global_config import JWT_HEADER_NAME, DBSession
from assets.http.schema import asset_graphql_app
from authentication.tests.auth_test import TestAuthenticationController
from assets.db_models.asset import AssetModel
from stages.tests.test_stage import TestStageController
from stages.db_models.stage import StageModel
from users.db_models.user import UserModel


def load_base64_from_image(image_path):
    with open(image_path, "rb") as image_file:
        base64_encoded = base64.b64encode(image_file.read()).decode("utf-8")
    return base64_encoded


app.mount("/asset_graphql", asset_graphql_app)
test_AuthenticationController = TestAuthenticationController()
test_stageController = TestStageController()


@pytest.mark.anyio
class TestAssetController:
    mutation_query = """
        mutation UploadFile($base64: String!, $filename: String!) {
            uploadFile(base64: $base64, filename: $filename) {
                url
            }
        }
    """

    async def test_01_upload_file_successfully(self, client):
        data = await test_AuthenticationController.test_02_login_successfully(client)

        headers = {
            "Authorization": f'Bearer {data["data"]["login"]["access_token"]}',
            JWT_HEADER_NAME: data["data"]["login"]["refresh_token"],
        }

        variables = {
            "base64": f"data:image/jpeg;base64,{load_base64_from_image('src/assets/tests/images/test.png')}",
            "filename": "test.png",
        }
        response = client.post(
            "/asset_graphql",
            json={"query": self.mutation_query, "variables": variables},
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "uploadFile" in data["data"]
        assert "url" in data["data"]["uploadFile"]
        assert data["data"]["uploadFile"]["url"] is not None

    async def test_02_upload_file_without_authentication(self, client):
        variables = {
            "base64": f"data:image/jpeg;base64,{load_base64_from_image('src/assets/tests/images/test.png')}",
            "filename": "test.png",
        }
        response = client.post(
            "/asset_graphql",
            json={"query": self.mutation_query, "variables": variables},
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "errors" in data
        assert data["errors"][0]["message"] == "Authenticated Failed"

    async def test_03_save_media_successfully(self, client):
        data = await test_AuthenticationController.test_02_login_successfully(client)
        assigned_user = await test_AuthenticationController.test_02_login_successfully(
            client
        )

        headers = {
            "Authorization": f'Bearer {data["data"]["login"]["access_token"]}',
            JWT_HEADER_NAME: data["data"]["login"]["refresh_token"],
        }

        mutation_query = """
            mutation SaveMedia($input: SaveMediaInput!) {
                saveMedia(input: $input) {
                    asset {
                        id
                    }
                }
            }
        """

        stage = await test_stageController.test_01_create_stage(client)

        variables = {
            "input": {
                "name": "test",
                "mediaType": "image",
                "urls": ["https://test.com/test.png?download/media"],
                "w": 100,
                "h": 100,
                "tags": ["test"],
                "copyrightLevel": 0,
                "stageIds": [stage["id"]],
                "userIds": [assigned_user["data"]["login"]["user_id"]],
                "owner": data["data"]["login"]["username"],
            }
        }
        response = client.post(
            "/asset_graphql",
            json={"query": mutation_query, "variables": variables},
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "saveMedia" in data["data"]
        assert "id" in data["data"]["saveMedia"]["asset"]

    async def test_04_save_media_without_authentication(self, client):
        mutation_query = """
            mutation SaveMedia($input: SaveMediaInput!) {
                saveMedia(input: $input) {
                    asset {
                        id
                    }
                }
            }
        """

        stages = DBSession.query(StageModel).all()
        users = DBSession.query(UserModel).all()

        variables = {
            "input": {
                "name": "test",
                "mediaType": "image",
                "urls": ["https://test.com/test.png"],
                "w": 100,
                "h": 100,
                "tags": ["test"],
                "copyrightLevel": 0,
                "stageIds": [stage.id for stage in stages],
                "userIds": [user.id for user in users],
                "owner": "test",
            }
        }
        response = client.post(
            "/asset_graphql",
            json={"query": mutation_query, "variables": variables},
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "errors" in data
        assert data["errors"][0]["message"] == "Authenticated Failed"

    async def test_05_search_assets(self, client):
        data = await test_AuthenticationController.test_02_login_successfully(client)
        asset = DBSession.query(AssetModel).join(UserModel).first()
        headers = {
            "Authorization": f'Bearer {data["data"]["login"]["access_token"]}',
            JWT_HEADER_NAME: data["data"]["login"]["refresh_token"],
        }

        query = """
            query ($input: MediaTableInput!) {
                media(input: $input) {
                    totalCount
                    edges {
                        id
                        name
                    }
                }
            }
        """

        users = DBSession.query(UserModel).all()
        stages = DBSession.query(StageModel).all()

        response = client.post(
            "/asset_graphql",
            json={
                "query": query,
                "variables": {
                    "input": {
                        "page": 1,
                        "limit": 10,
                        "sort": [
                            "ASSET_TYPE_ID_ASC",
                            "OWNER_ID_DESC",
                            "CREATED_ON_ASC",
                            "NAME_ASC",
                        ],
                        "name": "test",
                        "mediaTypes": ["image"],
                        "owners": [user.username for user in users],
                        "stages": [stage.id for stage in stages],
                        "tags": ["test"],
                        "createdBetween": ["2021-01-01", "2026-12-31"],
                    }
                },
            },
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "media" in data["data"]
        assert "totalCount" in data["data"]["media"]
        assert "edges" in data["data"]["media"]
        assert len(data["data"]["media"]["edges"]) > 0

    async def test_06_get_all_medias(self, client):
        data = await test_AuthenticationController.test_02_login_successfully(client)
        asset = DBSession.query(AssetModel).join(UserModel).first()
        headers = {
            "Authorization": f'Bearer {data["data"]["login"]["access_token"]}',
            JWT_HEADER_NAME: data["data"]["login"]["refresh_token"],
        }

        query = """
            query mediaList($mediaType: String, $owner: String) {
                mediaList(mediaType: $mediaType, owner: $owner) {
                        id
                        name
                        assetType {
                            name
                        }
                        owner {
                            id
                            username
                        }

                }
            }
        """

        response = client.post(
            "/asset_graphql",
            json={
                "query": query,
                "variables": {"mediaType": "image", "owner": asset.owner.username},
            },
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "mediaList" in data["data"]
        assert len(data["data"]["mediaList"]) > 0

    async def test_07_update_media(self, client):
        data = await test_AuthenticationController.test_02_login_successfully(client)
        asset = DBSession.query(AssetModel).join(UserModel).first()

        headers = {
            "Authorization": f'Bearer {data["data"]["login"]["access_token"]}',
            JWT_HEADER_NAME: data["data"]["login"]["refresh_token"],
        }

        mutation_query = """
            mutation SaveMedia($input: SaveMediaInput!) {
                saveMedia(input: $input) {
                    asset {
                        id
                    }
                }
            }
        """

        variables = {
            "input": {
                "id": asset.id,
                "name": "test",
                "mediaType": "image",
                "urls": ["https://test.com/test.png?download/media"],
                "w": 100,
                "h": 100,
                "tags": ["test"],
                "copyrightLevel": 0,
                "stageIds": [],
                "userIds": [],
                "owner": data["data"]["login"]["username"],
            }
        }
        response = client.post(
            "/asset_graphql",
            json={"query": mutation_query, "variables": variables},
            headers=headers,
        )

        assert response.status_code == 200

    async def test_08_update_media_failed(self, client):
        data = await test_AuthenticationController.test_player_login_successfully(
            client
        )
        asset = DBSession.query(AssetModel).join(UserModel).first()

        headers = {
            "Authorization": f'Bearer {data["data"]["login"]["access_token"]}',
            JWT_HEADER_NAME: data["data"]["login"]["refresh_token"],
        }

        mutation_query = """
            mutation SaveMedia($input: SaveMediaInput!) {
                saveMedia(input: $input) {
                    asset {
                        id
                    }
                }
            }
        """

        variables = {
            "input": {
                "id": asset.id,
                "name": "test",
                "mediaType": "image",
                "urls": ["https://test.com/test.png?download/media"],
                "w": 100,
                "h": 100,
                "tags": ["test"],
                "copyrightLevel": 0,
                "stageIds": [],
                "userIds": [],
                "owner": data["data"]["login"]["username"],
            }
        }
        response = client.post(
            "/asset_graphql",
            json={"query": mutation_query, "variables": variables},
            headers=headers,
        )

        assert response.status_code == 200

    async def test_09_delete_media_failed(self, client):
        asset = DBSession.query(AssetModel).first()
        data = await test_AuthenticationController.test_player_login_successfully(
            client
        )

        headers = {
            "Authorization": f'Bearer {data["data"]["login"]["access_token"]}',
            JWT_HEADER_NAME: data["data"]["login"]["refresh_token"],
        }

        mutation_query = """
            mutation DeleteMedia($id: ID!) {
                deleteMedia(id: $id) {
                    success
                }
            }
        """

        variables = {"id": asset.id}
        client.post(
            "/asset_graphql",
            json={"query": mutation_query, "variables": variables},
            headers=headers,
        )

        data = await test_AuthenticationController.test_02_login_successfully(client)
        headers = {
            "Authorization": f'Bearer {data["data"]["login"]["access_token"]}',
            JWT_HEADER_NAME: data["data"]["login"]["refresh_token"],
        }

        response = client.post(
            "/asset_graphql",
            json={"query": mutation_query, "variables": {"id": 12}},
            headers=headers,
        )

        assert response.status_code == 200

    async def test_10_delete_media(self, client):
        asset = DBSession.query(AssetModel).first()
        data = await test_AuthenticationController.test_02_login_successfully(client)
        headers = {
            "Authorization": f'Bearer {data["data"]["login"]["access_token"]}',
            JWT_HEADER_NAME: data["data"]["login"]["refresh_token"],
        }

        mutation_query = """
            mutation DeleteMedia($id: ID!) {
                deleteMedia(id: $id) {
                    success
                }
            }
        """

        variables = {"id": asset.id}
        response = client.post(
            "/asset_graphql",
            json={"query": mutation_query, "variables": variables},
            headers=headers,
        )
        assert response.status_code == 200

        asset = DBSession.query(AssetModel).filter_by(id=asset.id).first()
        assert asset is None

    async def test_11_upload_file_with_large_file(self, client):
        data = await test_AuthenticationController.test_02_login_successfully(client)

        headers = {
            "Authorization": f'Bearer {data["data"]["login"]["access_token"]}',
            JWT_HEADER_NAME: data["data"]["login"]["refresh_token"],
        }

        variables = {
            "base64": f"data:image/jpeg;base64,{load_base64_from_image('src/assets/tests/images/large-file.jpg')}",
            "filename": "large-file.jpg",
        }
        response = client.post(
            "/asset_graphql",
            json={"query": self.mutation_query, "variables": variables},
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "errors" in data
        assert data["errors"][0]["message"] == "Image files must be under 1MB."
