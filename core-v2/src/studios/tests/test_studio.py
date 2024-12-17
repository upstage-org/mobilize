import random
from faker import Faker
import pytest
from authentication.tests.auth_test import TestAuthenticationController
from assets.db_models.asset import AssetModel
from assets.db_models.asset_usage import AssetUsageModel
from stages.db_models.stage import StageModel
from stages.tests.test_stage import TestStageController
from studios.http.schema import studio_graphql_app
from users.db_models.user import GUEST, PLAYER, SUPER_ADMIN, UserModel
from global_config import DBSession, ScopedSession
from src.main import app

test_AuthenticationController = TestAuthenticationController()
test_StageController = TestStageController()

app.mount("/studio_graphql", studio_graphql_app)


@pytest.mark.anyio
class TestStudioController:
    async def test_01_create_users(self, client):
        headers = test_AuthenticationController.get_headers(client, SUPER_ADMIN)
        query = """
            mutation batchUserCreation($users: [BatchUserInput]!) {
                batchUserCreation(users: $users) {
                    users {
                        username
                        email
                        role
                        firstName
                        lastName
                        createdOn
                    }
                }
            }
        """
        email = f"{random.randint(1, 1000)}{Faker().email()}"
        username = f"test_user_{random.randint(1, 1000)}"

        variables = {
            "users": [
                {"username": username, "password": "password", "email": email},
                {
                    "username": f"test_user_{random.randint(1, 1000)}",
                    "password": "password",
                    "email": f"{random.randint(1, 1000)}{Faker().email()}",
                },
            ],
        }

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200
        assert "data" in response.json()
        assert "batchUserCreation" in response.json()["data"]
        assert "users" in response.json()["data"]["batchUserCreation"]

        variables = {
            "users": [
                {
                    "username": username,
                    "password": "password",
                    "email": f"{random.randint(1, 1000)}{Faker().email()}",
                },
            ],
        }

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200
        assert "errors" in response.json()

        variables = {
            "users": [
                {"username": "test_user", "password": "password", "email": email},
                {"username": "test_user", "password": "password", "email": email},
            ],
        }

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200
        assert "errors" in response.json()

    async def test_02_update_user(self, client):
        username = None
        with ScopedSession() as session:
            user = session.query(UserModel).first()
            user.active = False
            username = user.username
            session.flush()

        user = DBSession.query(UserModel).filter(UserModel.username == username).first()

        headers = test_AuthenticationController.get_headers(client, SUPER_ADMIN)
        query = """
            mutation updateUser($input: UpdateUserInput!) {
                updateUser(input: $input) {
                        username
                        email
                }
            }
        """

        email = f"{random.randint(1, 1000)}{Faker().email()}"
        username = f"test_user_{random.randint(1, 1000)}"

        variables = {
            "input": {
                "id": user.id,
                "username": username,
                "password": "new_password",
                "email": email,
                "binName": "new_bin",
                "role": SUPER_ADMIN,
                "firstName": "Updated",
                "lastName": "User",
                "displayName": "Updated User",
                "active": True,
                "firebasePushnotId": "new_push_id",
                "uploadLimit": 100,
                "intro": "This is an updated user",
            }
        }

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200
        assert "data" in response.json()
        assert "updateUser" in response.json()["data"]
        assert "email" in response.json()["data"]["updateUser"]

        variables = {
            "input": {
                **variables["input"],
                "password": None,
                "active": False,
            }
        }

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200
        assert "data" in response.json()
        assert "updateUser" in response.json()["data"]
        assert "email" in response.json()["data"]["updateUser"]

        variables = {"input": {**variables["input"], "id": 1000}}

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200
        assert "errors" in response.json()

        variables = {
            "input": {
                **variables["input"],
                "email": None,
            }
        }

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200
        assert "errors" in response.json()

        user_2 = DBSession.query(UserModel).all()[-1]

        variables = {
            "input": {
                **variables["input"],
                "id": user.id,
                "email": user_2.email,
            }
        }

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200
        assert "errors" in response.json()

    async def test_03_admin_players(self, client):
        headers = test_AuthenticationController.get_headers(client, SUPER_ADMIN)
        query = """
            query adminPlayers($first: Int,$page: Int,$sort: [AdminPlayerSortEnum],$usernameLike: String, $createdBetween: [String]) {
                adminPlayers(first: $first, page: $page, sort: $sort, usernameLike: $usernameLike, createdBetween: $createdBetween) {
                    totalCount
                    edges {
                    email
                    username
                    }
                }
            }
        """

        variables = {
            "first": 10,
            "page": 1,
            "sort": [
                "USERNAME_ASC",
                "CREATED_ON_DESC",
                "USERNAME_DESC",
                "CREATED_ON_ASC",
            ],
            "usernameLike": "@",
            "createdBetween": ["2021-01-01", "2025-12-31"],
        }

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200
        assert "data" in response.json()
        assert "adminPlayers" in response.json()["data"]
        assert "totalCount" in response.json()["data"]["adminPlayers"]
        assert "username" in response.json()["data"]["adminPlayers"]["edges"][0]
        assert "email" in response.json()["data"]["adminPlayers"]["edges"][0]

    async def test_04_delete_user(self, client):
        headers = test_AuthenticationController.get_headers(client, SUPER_ADMIN)
        user = DBSession.query(UserModel).all()[-1]

        query = """
            mutation deleteUser($id: ID!) {
                deleteUser(id: $id) {
                        success
                    }
                }
        """

        variables = {"id": user.id}

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200
        assert "data" in response.json()
        assert "deleteUser" in response.json()["data"]
        assert "success" in response.json()["data"]["deleteUser"]
        headers = test_AuthenticationController.get_headers(client, SUPER_ADMIN)
        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200
        assert "errors" in response.json()

    async def test_05_change_password(self, client):
        headers = test_AuthenticationController.get_headers(client, SUPER_ADMIN)
        user = DBSession.query(UserModel).all()[-1]

        query = """
            mutation changePassword($input: ChangePasswordInput!) {
                changePassword(input: $input) {
                        success
                    }
                }
        """

        variables = {
            "input": {
                "id": user.id,
                "oldPassword": "testpassword",
                "newPassword": "new_password",
            }
        }

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200
        assert "data" in response.json()
        assert "changePassword" in response.json()["data"]
        assert "success" in response.json()["data"]["changePassword"]

        variables = {
            "input": {
                "id": user.id,
                "oldPassword": "testpassword",
                "newPassword": "new_password",
            }
        }

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200
        assert "errors" in response.json()

        variables = {
            "input": {
                "id": 1000,
                "oldPassword": "testpassword",
                "newPassword": "new_password",
            }
        }

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200
        assert "errors" in response.json()

    async def test_06_calc_sizes(self, client):
        headers = test_AuthenticationController.get_headers(client, SUPER_ADMIN)
        query = """
            mutation calcSizes {
                calcSizes {
                        size
                    }
                }
        """

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query},
        )

        assert response.status_code == 200
        assert "data" in response.json()
        assert "calcSizes" in response.json()["data"]
        assert "size" in response.json()["data"]["calcSizes"]

    async def test_07_request_permission(self, client):
        headers = test_AuthenticationController.get_headers(client, SUPER_ADMIN)
        query = """
            mutation requestPermission($assetId: ID!, $note: String) {
                requestPermission(assetId: $assetId, note: $note) {
                        success
                        permissions {
                            id
                            userId
                            assetId
                            approved
                            seen
                            createdOn
                            note
                            user {
                                username
                                displayName
                            }
                        }
                    }
                }
        """

        asset = DBSession.query(AssetModel).first()

        variables = {
            "assetId": asset.id,
            "note": "This is a permission request",
        }

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200
        assert "data" in response.json()
        assert "requestPermission" in response.json()["data"]
        assert "success" in response.json()["data"]["requestPermission"]
        assert "permissions" in response.json()["data"]["requestPermission"]

        variables = {
            "assetId": 1000,
            "note": "This is a permission request",
        }

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200
        assert "errors" in response.json()

        with ScopedSession() as session:
            asset = session.query(AssetModel).first()
            asset.copyright_level = 2
            session.flush()
            variables = {
                "assetId": asset.id,
                "note": "This is a permission request",
            }

            response = client.post(
                "/studio_graphql",
                headers=headers,
                json={"query": query, "variables": variables},
            )

            assert response.status_code == 200
            assert "errors" not in response.json()
            assert "requestPermission" in response.json()["data"]
            assert "success" in response.json()["data"]["requestPermission"]
            assert "permissions" in response.json()["data"]["requestPermission"]

    async def test_08_confirm_permission(self, client):
        headers = test_AuthenticationController.get_headers(client, SUPER_ADMIN)
        player_headers = test_AuthenticationController.get_headers(client, PLAYER)
        query = """
            mutation confirmPermission($id: ID!, $approved: Boolean) {
                confirmPermission(id: $id, approved: $approved) {
                        success
                        permissions {
                            id
                            userId
                            assetId
                            approved
                            seen
                            createdOn
                            note
                            user {
                                username
                                displayName
                            }
                        }
                    }
                }
        """

        asset = DBSession.query(AssetUsageModel).all()[-1]

        variables = {
            "id": asset.id,
            "approved": True,
        }

        response = client.post(
            "/studio_graphql",
            headers=player_headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200
        assert "errors" in response.json()

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200
        assert "data" in response.json()
        assert "confirmPermission" in response.json()["data"]
        assert "success" in response.json()["data"]["confirmPermission"]
        assert "permissions" in response.json()["data"]["confirmPermission"]

        variables = {
            "id": 1000,
            "approved": True,
        }

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200
        assert "errors" in response.json()

        variables = {
            "id": asset.id,
            "approved": False,
        }

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200

    async def test_09_quick_assign_mutation(self, client):
        headers = test_AuthenticationController.get_headers(client, SUPER_ADMIN)
        query = """
            mutation quickAssignMutation($stageId: ID!, $assetId: ID!) {
                quickAssignMutation(stageId: $stageId, assetId: $assetId) {
                        success
                    }
                }
        """

        asset = DBSession.query(AssetModel).first()

        stage = DBSession.query(StageModel).first()

        variables = {
            "stageId": stage.id,
            "assetId": asset.id,
        }

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200
        assert "data" in response.json()
        assert "quickAssignMutation" in response.json()["data"]
        assert "success" in response.json()["data"]["quickAssignMutation"]

        variables = {
            "stageId": 1000,
            "assetId": asset.id,
        }

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200
        assert "errors" in response.json()

        variables = {
            "stageId": stage.id,
            "assetId": 1000,
        }

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200
        assert "errors" in response.json()

    async def test_10_whoami(self, client):
        headers = test_AuthenticationController.get_headers(client, SUPER_ADMIN)
        query = """
            query whoami {
                whoami {
                        username
                        email
                        role
                    }
                }
        """

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query},
        )

        assert response.status_code == 200
        assert "data" in response.json()
        assert "whoami" in response.json()["data"]
        assert "username" in response.json()["data"]["whoami"]
        assert "email" in response.json()["data"]["whoami"]
        assert "role" in response.json()["data"]["whoami"]

    async def test_11_send_email(self, client):
        headers = test_AuthenticationController.get_headers(client, SUPER_ADMIN)
        query = """
            mutation sendEmail($input: SendEmailInput!) {
                sendEmail(input: $input) {
                        success
                    }
                }
        """

        variables = {
            "input": {
                "recipients": Faker().email(),
                "subject": "Test Email",
                "body": "This is a test email",
                "bcc": "",
            }
        }

        response = client.post(
            "/studio_graphql",
            headers=headers,
            json={"query": query, "variables": variables},
        )

        assert response.status_code == 200
        assert "data" in response.json()
        assert "sendEmail" in response.json()["data"]
        assert "success" in response.json()["data"]["sendEmail"]
